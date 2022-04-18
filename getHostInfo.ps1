$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
# Get machine list
$excelFile = "C:\Users\bardend\OneDrive - Aspen Technology, Inc\QE VM Hosts\VM list.xlsx"
$hostList = Get-Content -Path "C:\Users\BARDEND\Desktop\newDash\hostList.txt"
$workingDIR = "C:\Users\BARDEND\Desktop\newDash\data"

# Do it forever
while ($true) {

    # Hit the spreadsheet
    $objExcel = New-Object -ComObject Excel.Application
    $objExcel.Visible = $False
    $objExcel.DisplayAlerts = $False
    $WorkBook = $objExcel.Workbooks.Open($excelFile)
    $xlCSV = 6
    $sheetNames = ($WorkBook.sheets | Select-Object -Property Name).Name
    foreach ($Sheet in $sheetNames) {
        $WorkSheet = $WorkBook.sheets.item("$Sheet")
        $csv = Join-Path $workingDIR "user_$Sheet.csv"
        $WorkSheet.SaveAs($csv,$xlCSV)
    }
    $objExcel.quit()

    # For each machine
    foreach ($h in $hostList) {
        # Outfiles
        $hyperVFile = Join-Path $workingDIR "hyperV_$($h).csv"
        $diskInfoFile = Join-Path $workingDIR "diskInfo_$($h).csv"
        $adminListFile = Join-Path $workingDIR "adminList_$($h).csv"

        # Open a session
        $session = New-PSSession -ComputerName $h

        # Get Hyper V Info
        $hyperV = Invoke-Command -Session $session -ScriptBlock {
            '"VM Name","Drive","VM Size (GB)"'
            $vmList = Get-VM
            foreach ($vm in $vmList) {
                # Get all files in the path
                $allFiles = @()
                $allFiles += Get-ChildItem (split-path -parent $vm.HardDrives.Path)
                $allFiles += Get-ChildItem (Join-Path $vm.SmartPagingFilePath "\Snapshots") -Recurse
                $allFiles += Get-ChildItem (Join-Path $vm.SmartPagingFilePath "\Virtual Machines") -Recurse
                $allFiles += Get-ChildItem (Join-Path $vm.SnapshotFileLocation "\Snapshots") -Recurse
                $allFiles += Get-ChildItem (Join-Path $vm.SnapshotFileLocation "\Virtual Machines") -Recurse
                $vmSizeGB = ($allFiles | Sort-Object | Get-Unique | Measure-Object -Property Length -Sum).Sum/1GB
                "`"$($vm.Name)`",`"$(Split-Path -Path $vm.HardDrives.Path -Qualifier)`",`"$([math]::Round($vmSizeGB,2))`""   
            }
        }
        $hyperV > $hyperVFile

        # Get Disk Info
        $diskInfo = Invoke-Command -Session $session -ScriptBlock {
            $diskList = get-WmiObject win32_logicaldisk
            '"Drive","Free Space (GB)","Drive Size (GB)"'
            foreach ($disk in $diskList) {
                "`"$($disk.DeviceID)`",`"$([math]::Round($disk.FreeSpace/1GB,2))`",`"$([math]::Round($disk.Size/1GB,2))`""
            }
        }
        $diskInfo > $diskInfoFile

        # Get Admin List
        $adminList = Invoke-Command -Session $session -ScriptBlock {
            net localgroup administrators
        } | sls 'CORP'
        "Admin List" > $adminListFile
        foreach ($admin in $adminList) {
            $admin >> $adminListFile
        }

        # Remove Session
        $session | Remove-PSSession

    }

    # Sleep
    Start-Sleep -Seconds 300
}
