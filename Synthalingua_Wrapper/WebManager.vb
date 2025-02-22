Public Class WebManager
    Public Shared Function GetWebLink(portNumber As Integer, linkType As String) As String
        Return $"http://localhost:{portNumber}?show{linkType}"
    End Function

    Public Shared Sub CopyWebLinkToClipboard(portNumber As Integer, linkType As String)
        Dim url As String = GetWebLink(portNumber, linkType)
        Clipboard.SetText(url)
        MessageBox.Show($"Copied {url} to clipboard")
    End Sub

    Public Shared Sub OpenSocialLink(url As String)
        Process.Start(New ProcessStartInfo(url) With {.UseShellExecute = True})
    End Sub

    Public Shared Function ValidateHLSPassword(url As String, showPassword As Boolean) As String
        If showPassword Then
            Return New String("*"c, url.Length)
        End If
        Return url
    End Function

    Public Shared Sub ShowSubtitleWindow(webServerEnabled As Boolean, subtitleWindow As Form)
        If webServerEnabled Then
            subtitleWindow.Show()
        Else
            MessageBox.Show("Please enable the web server to use this feature.")
        End If
    End Sub
End Class