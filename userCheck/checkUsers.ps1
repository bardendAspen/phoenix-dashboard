Param($machineDNS)
$phxConfig = 'C:\PhoenixControl\MissionControl\configFiles\phxConfig.csv'
$dataPath = 'C:\PhoenixControl\MissionControl\dataRepo'

#$machineDNS = "PHX-S16-V122.qae.aspentech.com"
$machine = $machineDNS.Split('.')[0]

$usersFile = Join-Path $dataPath "$($machine)\users.csv"
$statusFile = Join-Path $dataPath "$($machine)\status.csv"

function getUsers {
    param ($psSession)
    try {
        Invoke-Command -Session $psSession -ScriptBlock {quser} -ErrorAction Stop
    }
    catch {
        return $_.ToString()
    }
}

function updateUsersCSV {
    param ($csvString)
    '"Active Users","User 1","User 2"' > $usersFile
    $csvString >> $usersFile
}


while($true) {
    # Get status
    $status = (Import-Csv -Path $statusFile).Status
    # Create a session and enter a loop if ready
    if ($status -eq 'Ready') {
        # Create new Session
        try {
            # Try to open a session
            $session = New-PSSession $machineDNS
        }
        catch {
            # Session failed, $null it
            $session = $null
        }
        # Enter check loop
        $checkLoop = $true
        while ($checkLoop) {
            # Ping quser
            $quserOut = getUsers($session)
            # Check for object type output for non error return
            if ($quserOut.GetType().Name -eq "Object[]") {
                # Get Active Users
                $activeUsers = $quserOut | select-string "Active"
                # Check User 1
                if ($null -ne  $activeUsers) {$u1Line = $activeUsers[0]} else {$u1Line = $null}
                if ($null -ne  $activeUsers) {$u2Line = $activeUsers[1]} else {$u2Line = $null}
                if ($null -ne $u1Line) {$u1 = $u1Line.Line.Split(' ')[1]} else {$u1 = " "}
                if ($null -ne $u2Line) {$u2 = $u2Line.Line.Split(' ')[1]} else {$u2 = " "}
                #if ((($quserOut | select-string "Active") | Select-String "qahee").Count -gt 0) {$qahee = "Active"} else {$qahee = " "}
                # Check User 2
                #if ((($quserOut | select-string "Active") | Select-String "qapart").Count -gt 0) {$qapart = "Active"} else {$qapart = " "}
                # Update the users
                updateUsersCSV("`"$($activeUsers.Count)`",`"$($u1)`",`"$($u2)`"")
            } else {
                # Check for error types
                if ($quserOut.Contains("No User exists")) {
                    # No Users
                    updateUsersCSV('"0"," "," "')
                } elseif ($quserOut.Contains("session state is Broken")) {
                    # Broken Session Remove and exit
                    # Update Users
                    updateUsersCSV('"-","-","-"')
                    # Remove Session
                    $session | Remove-PSSession
                    # Exit loop
                    $checkLoop = $false
                    
                } elseif ($quserOut.Contains("Cannot validate argument on parameter")) {
                    # Broken Session Remove and exit
                    # Update Users
                    updateUsersCSV('"-","-","-"')
                    # Remove Session
                    $session | Remove-PSSession
                    # Exit loop
                    $checkLoop = $false
                } else {
                    # Assume Broken Session but report unknown scenario
                    "Unknown Scenario: $($quserOut)"
                    # Update Users
                    updateUsersCSV('"-","-","-"')
                    # Remove Session
                    $session | Remove-PSSession
                    # Exit loop
                    $checkLoop = $false
                }
                
            }
            Start-Sleep -Seconds 5
            # Check status for changes before repeating
            $status = (Import-Csv -Path $statusFile).Status
            if ($status -ne 'Ready') {
                # Machine is no longer ready
                # Update Users
                updateUsersCSV('"-","-","-"')
                # Remove Session
                $session | Remove-PSSession
                # Exit loop
                $checkLoop = $false
            }
        }
    } else {
        # Update Users
        updateUsersCSV('"-","-","-"')
        # Sleep for 5 and check again
        Start-Sleep -Seconds 5
    }
}