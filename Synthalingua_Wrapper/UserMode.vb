Public Class UserMode
    Private Sub AdvBtn_Click(sender As Object, e As EventArgs) Handles AdvBtn.Click
        MainUI.Show()
        Me.Close()
    End Sub

    Private Sub SimpleBtn_Click(sender As Object, e As EventArgs) Handles SimpleBtn.Click
        BasicMode.Show()
        Me.Close()
    End Sub
End Class