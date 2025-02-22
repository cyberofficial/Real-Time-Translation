Imports System.IO
Imports System.Net.Http
Imports System.Net.Sockets
Imports System.Runtime.InteropServices
Imports System.Security.Cryptography.X509Certificates
Imports System.Text
Imports System.Text.RegularExpressions
Imports System.Threading


Public Class subtitlewindow
    Private httpClient As HttpClient
    Private cts As CancellationTokenSource

    Private URLHeader As String
    Private URLTranslatedHeader As String
    Private URLTranscribedHeader As String

    Private iOriginalText As Boolean = False
    Private iTranscribeText As Boolean = False
    Private iTranslateText As Boolean = False

    Dim RTL_Mode As Boolean = False
    Dim Main_BG_COLOR As System.Drawing.Color = Color.FromArgb(0, 177, 64)

    Dim resizing As Boolean = False
    Dim resizableCorner As String = ""
    Dim startPoint As Point
    Dim startSize As Size
    Dim startLocation As Point
    Dim endPoint As Point

    Dim Dragable As Boolean = False

    Dim BackGroundToggle As Boolean = False

    Dim Rendering As Boolean = False
    Dim RenderingTransparency As Boolean = True

    <DllImport("user32.dll")>
    Public Shared Function SendMessage(hWnd As IntPtr, Msg As Integer, wParam As Integer, lParam As Integer) As Integer
    End Function

    <DllImport("user32.dll")>
    Public Shared Function ReleaseCapture() As Boolean
    End Function

    Public Sub New()
        Dim CaptionsHost As String = "localhost"
        InitializeComponent()
        httpClient = New HttpClient()
        cts = New CancellationTokenSource()
        Dim SubPortNumber As String = MainUI.PortNumber.Value.ToString()
        URLHeader = $"http://{CaptionsHost}:{SubPortNumber}/update-header"
        URLTranslatedHeader = $"http://{CaptionsHost}:{SubPortNumber}/update-translated-header"
        URLTranscribedHeader = $"http://{CaptionsHost}:{SubPortNumber}/update-transcribed-header"
        InitializeLabelWrapping(headertextlbl)
    End Sub

    Private Sub InitializeLabelWrapping(label As Label)
        label.AutoEllipsis = True
        label.MaximumSize = New Size(ClientSize.Width, 0)
    End Sub

    Private Function CountBlacklistedPhrases() As Integer
        Dim numberOfPhrases As Integer = 0

        Try
            Dim lines As String() = File.ReadAllLines(MainUI.WordBlockListLocation.ToString)
            numberOfPhrases = lines.Length
        Catch ex As Exception
            Debug.WriteLine("Error counting blacklisted phrases: " & ex.Message)
        End Try
        Return numberOfPhrases
    End Function

    Private Sub subtitlewindow_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        InfoSaverTimer.Interval = 25
        InfoSaverTimer.Start()
        Dim numberOfPhrases As Integer = CountBlacklistedPhrases()
        With headertextlbl
            .Font = My.Settings.headertextlbl_font
            .ForeColor = My.Settings.headertextlbl_forecolor
            .BackColor = My.Settings.headertextlbl_backcolor
        End With
        If My.Settings.subwindow_lmode = True Then
            headertextlbl.RightToLeft = RightToLeft.Yes
        End If

        Me.BackColor = My.Settings.subwindow_bgcolor

    End Sub
    Private Sub subtitlewindow_Resize(sender As Object, e As EventArgs) Handles MyBase.Resize
        Dim maxWidth = ClientSize.Width
        headertextlbl.MaximumSize = New Size(maxWidth, 0)
    End Sub

    Private Sub subtitlewindow_FormClosing(sender As Object, e As FormClosingEventArgs) Handles MyBase.FormClosing
        InfoSaverTimer.Stop()
        cts.Cancel()
        httpClient.Dispose()
        cts.Dispose()
        Me.Dispose()
    End Sub

    Private Async Sub InfoSaverTimer_Tick(sender As Object, e As EventArgs) Handles InfoSaverTimer.Tick
        If IsDisposed OrElse Disposing Then
            Return
        End If
        If Rendering = False Then
            headertextlbl.Text = "dummy text"
            Rendering = True
        End If
        Dim headerText As String = String.Empty
        Dim translatedHeaderText As String = String.Empty
        Dim transcribedHeaderText As String = String.Empty
        Try
            If iOriginalText = True Then
                headerText = Await FetchTextFromUrl(URLHeader, cts.Token)
                Debug.WriteLine("Header Text: " & headerText)
            End If
        Catch ex As Exception
            Debug.WriteLine("Error fetching header text: " & ex.Message)
        End Try
        Try
            If iTranslateText = True Then
                translatedHeaderText = Await FetchTextFromUrl(URLTranslatedHeader, cts.Token)
                Debug.WriteLine("Translated Header Text: " & translatedHeaderText)
            End If
        Catch ex As Exception
            Debug.WriteLine("Error fetching translated header text: " & ex.Message)
        End Try
        Try
            If iTranscribeText = True Then
                transcribedHeaderText = Await FetchTextFromUrl(URLTranscribedHeader, cts.Token)
                Debug.WriteLine("Transcribed Header Text: " & transcribedHeaderText)
            End If
        Catch ex As Exception
            Debug.WriteLine("Error fetching transcribed header text: " & ex.Message)
        End Try
        headerText = RemoveBlacklistedPhrases(headerText)
        translatedHeaderText = RemoveBlacklistedPhrases(translatedHeaderText)
        transcribedHeaderText = RemoveBlacklistedPhrases(transcribedHeaderText)

        If Not IsDisposed AndAlso Not Disposing AndAlso IsHandleCreated Then
            Try
                Invoke(Sub()
                           Dim displayText As String = String.Empty

                           If iOriginalText Then
                               displayText &= headerText
                           End If

                           If iTranslateText Then
                               If Not String.IsNullOrEmpty(displayText) Then
                                   displayText &= vbCrLf
                               End If
                               displayText &= translatedHeaderText
                           End If
                           If iTranscribeText Then
                               If Not String.IsNullOrEmpty(displayText) Then
                                   displayText &= vbCrLf
                               End If
                               displayText &= transcribedHeaderText
                           End If
                           headertextlbl.Text = displayText
                       End Sub)
            Catch ex As InvalidOperationException
                Debug.WriteLine("InvalidOperationException: " & ex.Message)
            Catch ex As Exception
                Debug.WriteLine("General Exception: " & ex.Message)
            End Try
        End If

        If Not IsDisposed AndAlso Not Disposing AndAlso IsHandleCreated Then
            Try
                Invoke(Sub()
                           Dim displayText As String = String.Empty
                           If iOriginalText Then
                               displayText &= headerText
                           End If
                           If iTranslateText Then
                               If Not String.IsNullOrEmpty(displayText) Then
                                   displayText &= vbCrLf
                               End If
                               displayText &= translatedHeaderText
                           End If
                           If iTranscribeText Then
                               If Not String.IsNullOrEmpty(displayText) Then
                                   displayText &= vbCrLf
                               End If
                               displayText &= transcribedHeaderText
                           End If
                           headertextlbl.Text = displayText
                           headertextlbl.Invalidate()
                           Refresh()
                       End Sub)
            Catch ex As InvalidOperationException
                Debug.WriteLine("InvalidOperationException: " & ex.Message)
            Catch ex As Exception
                Debug.WriteLine("General Exception: " & ex.Message)
            End Try
        End If
    End Sub

    Private Function RemoveBlacklistedPhrases(text As String) As String
        Dim blacklistedPhrases As List(Of String) = LoadBlacklistedPhrases()
        If MainUI.WordBlockList.Checked = True Then
            Dim words As String() = text.Split(" "c)

            Dim convertToStars As Boolean = convert_text_to_stars.Checked
            Dim convertToEmpty As Boolean = convert_text_to_empty.Checked

            For i As Integer = 0 To words.Length - 1
                For Each phrase As String In blacklistedPhrases
                    If words(i).IndexOf(phrase, StringComparison.OrdinalIgnoreCase) <> -1 Then
                        If convertToStars Then
                            words(i) = "*"
                        ElseIf convertToEmpty Then
                            words(i) = " "
                        End If
                        Exit For
                    End If
                Next
            Next
            text = String.Join(" ", words)
        End If

        Return text
    End Function


    Private Function LoadBlacklistedPhrases() As List(Of String)
        Dim blacklistedPhrases As New List(Of String)()
        Try
            Dim lines As String() = File.ReadAllLines(MainUI.WordBlockListLocation)
            For Each line As String In lines
                blacklistedPhrases.Add(line.Trim())
            Next
        Catch ex As Exception
            Debug.WriteLine("Error loading blacklisted phrases: " & ex.Message)
        End Try

        Return blacklistedPhrases
    End Function

    Private Async Function FetchTextFromUrl(url As String, ct As CancellationToken) As Task(Of String)
        Try
            Return Await httpClient.GetStringAsync(url, ct)
        Catch ex As OperationCanceledException
            Debug.WriteLine("Operation canceled")
            Return "Operation canceled"
        Catch ex As HttpRequestException
            Debug.WriteLine("HttpRequestException: " & ex.Message)
            Return "Error: " & ex.Message
        Catch ex As SocketException
            Debug.WriteLine("SocketException: " & ex.Message)
            Return "Error: " & ex.Message
        Catch ex As Exception
            Debug.WriteLine("General Exception: " & ex.Message)
            Return "Error: " & ex.Message
        End Try
    End Function

    Private Sub FontDialog1_Apply(sender As Object, e As EventArgs) Handles FontDialog1.Apply
        headertextlbl.Font = FontDialog1.Font
    End Sub

    Private Sub FontFaceToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles FontFaceToolStripMenuItem.Click
        If FontDialog1.ShowDialog() = DialogResult.OK Then
            headertextlbl.Font = FontDialog1.Font
        End If
    End Sub

    Private Sub PlantToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles PlantToolStripMenuItem.Click
        Dim unused = MessageBox.Show("Help: " + vbCrLf + "Click the icon in the task bar (the small icons next to your system clock) to restore or right click the caption box twice.", "Help Message")
        Main_BG_COLOR = Me.BackColor
        TransparencyKey = Me.BackColor
        FormBorderStyle = FormBorderStyle.None
        TopMost = True
        MenuStrip1.Visible = False
        If RenderingTransparency = True Then
            Opacity = 0.7
        End If
        Dragable = True
    End Sub

    Private Sub FrontToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles FrontToolStripMenuItem.Click
        Dim colorDialog As New ColorDialog()
        If colorDialog.ShowDialog() = DialogResult.OK Then
            headertextlbl.ForeColor = colorDialog.Color
        End If
    End Sub

    Private Sub BackToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles BackToolStripMenuItem.Click
        Dim colorDialog As New ColorDialog()
        If colorDialog.ShowDialog() = DialogResult.OK Then
            headertextlbl.BackColor = colorDialog.Color
        End If
    End Sub

    Private Sub headertextlbl_MouseDoubleClick(sender As Object, e As MouseEventArgs) Handles headertextlbl.MouseDoubleClick
        TransparencyKey = Color.Empty
        BackColor = Main_BG_COLOR
        FormBorderStyle = FormBorderStyle.Sizable
        TopMost = False
        BringToFront()
        MenuStrip1.Visible = True
        Opacity = 1
        Dragable = False
        BackGroundToggle = False
    End Sub

    Private Sub SetTextVisibility(textType As String, visible As Boolean)
        Select Case textType
            Case "Original"
                iOriginalText = visible
            Case "Translate"
                iTranslateText = visible
            Case "Transcribe"
                iTranscribeText = visible
        End Select
    End Sub

    Private Sub ShowToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ShowToolStripMenuItem.Click
        SetTextVisibility("Original", True)
    End Sub

    Private Sub HideToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles HideToolStripMenuItem.Click
        SetTextVisibility("Original", False)
    End Sub

    Private Sub ShowToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles ShowToolStripMenuItem1.Click
        SetTextVisibility("Translate", True)
    End Sub

    Private Sub HideToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles HideToolStripMenuItem1.Click
        SetTextVisibility("Translate", False)
    End Sub

    Private Sub ShowToolStripMenuItem2_Click(sender As Object, e As EventArgs) Handles ShowToolStripMenuItem2.Click
        SetTextVisibility("Transcribe", True)
    End Sub

    Private Sub HideToolStripMenuItem2_Click(sender As Object, e As EventArgs) Handles HideToolStripMenuItem2.Click
        SetTextVisibility("Transcribe", False)
    End Sub

    Private Sub headertextlbl_MouseDown(sender As Object, e As MouseEventArgs) Handles headertextlbl.MouseDown
        If e.Button = MouseButtons.Left And Dragable = True Then
            Dim unused1 = ReleaseCapture()
            Dim unused = SendMessage(Handle, &H112, &HF012, 0)
        End If
        If e.Button = MouseButtons.Left And Dragable = False Then
            moving = True
            moveStartPoint = e.Location
        End If
    End Sub

    Private Sub LeftToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles LeftToolStripMenuItem1.Click
        headertextlbl.RightToLeft = RightToLeft.No
        RTL_Mode = False
    End Sub

    Private Sub RightToLeftToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles RightToLeftToolStripMenuItem.Click
        headertextlbl.RightToLeft = RightToLeft.Yes
        RTL_Mode = True
    End Sub


    Private Sub BG_Color_Click(sender As Object, e As EventArgs) Handles BG_Color.Click
        ColorDialog1.ShowDialog()
        Me.BackColor = ColorDialog1.Color
    End Sub

    Private Sub ResetBGColor_Click(sender As Object, e As EventArgs) Handles ResetBGColor.Click
        Me.BackColor = Color.FromArgb(0, 177, 64)
    End Sub

    Private Sub ResetCWindow_Click(sender As Object, e As EventArgs)

    End Sub

    Private Sub SaveToolStripMenuItem3_Click(sender As Object, e As EventArgs) Handles SaveToolStripMenuItem3.Click
        My.Settings.headertextlbl_font = headertextlbl.Font
        My.Settings.headertextlbl_forecolor = headertextlbl.ForeColor
        My.Settings.headertextlbl_backcolor = headertextlbl.BackColor
        My.Settings.subwindow_lmode = RTL_Mode
        My.Settings.subwindow_bgcolor = Me.BackColor
        My.Settings.Save()
        My.Settings.Reload()
        MessageBox.Show("Your captions window settings were saved.", "Saved")
    End Sub

    Private Sub ResetToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ResetToolStripMenuItem.Click
        With My.Settings
            .headertextlbl_font = New FontConverter().ConvertFromString(My.Settings.Properties("headertextlbl_font").DefaultValue.ToString())
            .translatedheaderlbl_font = New FontConverter().ConvertFromString(My.Settings.Properties("translatedheaderlbl_font").DefaultValue.ToString())
            .transcribedheaderlbl_font = New FontConverter().ConvertFromString(My.Settings.Properties("transcribedheaderlbl_font").DefaultValue.ToString())

            .headertextlbl_forecolor = Color.FromName(My.Settings.Properties("headertextlbl_forecolor").DefaultValue.ToString())
            .headertextlbl_backcolor = Color.FromName(My.Settings.Properties("headertextlbl_backcolor").DefaultValue.ToString())
            .translatedheaderlbl_forecolor = Color.FromName(My.Settings.Properties("translatedheaderlbl_forecolor").DefaultValue.ToString())
            .translatedheaderlbl_backcolor = Color.FromName(My.Settings.Properties("translatedheaderlbl_backcolor").DefaultValue.ToString())
            .transcribedheaderlbl_forecolor = Color.FromName(My.Settings.Properties("transcribedheaderlbl_forecolor").DefaultValue.ToString())
            .transcribedheaderlbl_backcolor = Color.FromName(My.Settings.Properties("transcribedheaderlbl_backcolor").DefaultValue.ToString())

            .subwindow_bgcolor = Color.FromName(My.Settings.Properties("subwindow_bgcolor").DefaultValue.ToString())

            .subwindow_lmode = False

            .Save()
            .Reload()
            Dim Cwindows As New subtitlewindow()
            Cwindows.Show()
            Me.Close()
        End With
    End Sub

    Private Function GetCornerType(x As Integer, y As Integer, width As Integer, height As Integer) As String
        Const CORNER_THRESHOLD As Integer = 10
        If x >= width - CORNER_THRESHOLD And y >= height - CORNER_THRESHOLD Then
            Return "bottom-right"
        ElseIf x <= CORNER_THRESHOLD And y >= height - CORNER_THRESHOLD Then
            Return "bottom-left"
        ElseIf x >= width - CORNER_THRESHOLD And y <= CORNER_THRESHOLD Then
            Return "top-right"
        ElseIf x <= CORNER_THRESHOLD And y <= CORNER_THRESHOLD Then
            Return "top-left"
        End If
        Return String.Empty
    End Function

    Private Function GetCornerCursor(cornerType As String) As Cursor
        Select Case cornerType
            Case "bottom-right", "top-left"
                Return Cursors.SizeNWSE
            Case "bottom-left", "top-right"
                Return Cursors.SizeNESW
            Case Else
                Return Cursors.Default
        End Select
    End Function

    Private Sub ResizePanel(corner As String, endPoint As Point)
        Select Case corner
            Case "bottom-right"
                Panel1.Size = New Size(startSize.Width + (endPoint.X - startPoint.X),
                                     startSize.Height + (endPoint.Y - startPoint.Y))
            Case "bottom-left"
                Panel1.Location = New Point(startLocation.X + (endPoint.X - startPoint.X), startLocation.Y)
                Panel1.Size = New Size(startSize.Width - (endPoint.X - startPoint.X),
                                     startSize.Height + (endPoint.Y - startPoint.Y))
            Case "top-right"
                Panel1.Location = New Point(startLocation.X, startLocation.Y + (endPoint.Y - startPoint.Y))
                Panel1.Size = New Size(startSize.Width + (endPoint.X - startPoint.X),
                                     startSize.Height - (endPoint.Y - startPoint.Y))
            Case "top-left"
                Panel1.Location = New Point(startLocation.X + (endPoint.X - startPoint.X),
                                          startLocation.Y + (endPoint.Y - startPoint.Y))
                Panel1.Size = New Size(startSize.Width - (endPoint.X - startPoint.X),
                                     startSize.Height - (endPoint.Y - startPoint.Y))
        End Select
    End Sub

    Private Sub Panel1_MouseDown(sender As Object, e As MouseEventArgs) Handles Panel1.MouseDown
        If e.Button = MouseButtons.Left Then
            resizableCorner = GetCornerType(e.X, e.Y, Panel1.Width, Panel1.Height)
            If resizableCorner <> String.Empty Then
                resizing = True
                startPoint = e.Location
                startSize = Panel1.Size
                startLocation = Panel1.Location
            End If
        End If
    End Sub

    Private Sub Panel1_MouseMove(sender As Object, e As MouseEventArgs) Handles Panel1.MouseMove
        If resizing Then
            Me.Opacity = 0.7
            Panel1.Cursor = Cursors.Cross
        Else
            Dim corner = GetCornerType(e.X, e.Y, Panel1.Width, Panel1.Height)
            Panel1.Cursor = GetCornerCursor(corner)
        End If
    End Sub

    Private Sub Panel1_MouseUp(sender As Object, e As MouseEventArgs) Handles Panel1.MouseUp
        If resizing Then
            endPoint = Panel1.PointToClient(MousePosition)
            ResizePanel(resizableCorner, endPoint)
            resizing = False
            resizableCorner = String.Empty
            Me.Opacity = 1
            Panel1.Cursor = Cursors.Default
        End If
    End Sub

    Private Sub MakeBackgroundInvisablToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles MakeBackgroundInvisablToolStripMenuItem.Click
        Me.TransparencyKey = Me.BackColor
        If BackGroundToggle = False Then
            Me.TransparencyKey = Me.BackColor
            BackGroundToggle = True
        Else
            Me.TransparencyKey = Color.Empty
            BackGroundToggle = False
        End If
    End Sub

    Private moving As Boolean = False
    Private moveStartPoint As Point

    Private Sub headertextlbl_MouseMove(sender As Object, e As MouseEventArgs) Handles headertextlbl.MouseMove
        If moving Then
            Dim newLocation As Point = Panel1.Location
            newLocation.Offset(e.X - moveStartPoint.X, e.Y - moveStartPoint.Y)
            Panel1.Location = newLocation
        End If
    End Sub

    Private Sub headertextlbl_MouseUp(sender As Object, e As MouseEventArgs) Handles headertextlbl.MouseUp
        If moving Then
            moving = False
        End If
    End Sub

    Private Sub SetTextAlignment(alignment As ContentAlignment)
        headertextlbl.TextAlign = alignment
    End Sub

    Private Sub LeftToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles LeftToolStripMenuItem.Click
        SetTextAlignment(ContentAlignment.TopLeft)
    End Sub

    Private Sub CenterToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles CenterToolStripMenuItem.Click
        SetTextAlignment(ContentAlignment.TopCenter)
    End Sub

    Private Sub RightToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles RightToolStripMenuItem.Click
        SetTextAlignment(ContentAlignment.TopRight)
    End Sub

    Private Sub LeftToolStripMenuItem2_Click(sender As Object, e As EventArgs) Handles LeftToolStripMenuItem2.Click
        SetTextAlignment(ContentAlignment.MiddleLeft)
    End Sub

    Private Sub CenterToolStripMenuItem3_Click(sender As Object, e As EventArgs) Handles CenterToolStripMenuItem3.Click
        SetTextAlignment(ContentAlignment.MiddleCenter)
    End Sub

    Private Sub RightToolStripMenuItem2_Click(sender As Object, e As EventArgs) Handles RightToolStripMenuItem2.Click
        SetTextAlignment(ContentAlignment.MiddleRight)
    End Sub

    Private Sub LeftToolStripMenuItem3_Click(sender As Object, e As EventArgs) Handles LeftToolStripMenuItem3.Click
        SetTextAlignment(ContentAlignment.BottomLeft)
    End Sub

    Private Sub CenterToolStripMenuItem2_Click(sender As Object, e As EventArgs) Handles CenterToolStripMenuItem2.Click
        SetTextAlignment(ContentAlignment.BottomCenter)
    End Sub

    Private Sub RightToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles RightToolStripMenuItem1.Click
        SetTextAlignment(ContentAlignment.BottomRight)
    End Sub

    Private Sub TransparentToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles TransparentToolStripMenuItem.Click
        headertextlbl.BackColor = Color.Empty
    End Sub

    Private Sub OnToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles OnToolStripMenuItem.Click
        headertextlbl.AutoSize = True
    End Sub

    Private Sub OffToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles OffToolStripMenuItem.Click
        headertextlbl.AutoSize = False
    End Sub

    Private Sub OffToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles OnToolStripMenuItem1.Click
        RenderingTransparency = False
    End Sub

    Private Sub OnToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles OffToolStripMenuItem1.Click
        RenderingTransparency = True
    End Sub

    Private Sub NotifyIcon1_MouseClick(sender As Object, e As MouseEventArgs) Handles NotifyIcon1.MouseClick
        If Dragable = True Then
            TransparencyKey = Color.Empty
            BackColor = Main_BG_COLOR
            FormBorderStyle = FormBorderStyle.Sizable
            TopMost = False
            BringToFront()
            MenuStrip1.Visible = True
            Opacity = 1
            Dragable = False
            BackGroundToggle = False
        End If
    End Sub

    Private Sub Panel1_MouseHover(sender As Object, e As EventArgs) Handles Panel1.MouseHover, headertextlbl.MouseHover
        Panel1.BackColor = Color.Blue
    End Sub

    Private Sub Panel1_MouseLeave(sender As Object, e As EventArgs) Handles Panel1.MouseLeave, headertextlbl.MouseLeave
        Panel1.BackColor = Me.BackColor
    End Sub
End Class
