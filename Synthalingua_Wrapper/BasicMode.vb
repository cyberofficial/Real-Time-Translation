Public Class BasicMode
    Private Sub LinkLabel1_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles LinkLabel1.LinkClicked
        Dim psi As New ProcessStartInfo
        psi.UseShellExecute = True
        psi.FileName = "https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks"
        Process.Start(psi)
    End Sub

    Private Sub DiscordWebHookBoxShowURLButton_Click(sender As Object, e As EventArgs) Handles DiscordWebHookBoxShowURLButton.Click
        If DiscordWebHookBox.UseSystemPasswordChar = False Then
            DiscordWebHookBox.UseSystemPasswordChar = True
        Else
            DiscordWebHookBox.UseSystemPasswordChar = False
        End If
    End Sub
End Class