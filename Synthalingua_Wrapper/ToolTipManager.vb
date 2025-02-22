Public Class ToolTipManager
    Private ReadOnly toolTip As ToolTip

    Public Sub New(tooltip As ToolTip)
        Me.toolTip = tooltip
    End Sub

    Public Sub SetWebLinkToolTip(control As Control, portNumber As Integer, linkType As String)
        toolTip.SetToolTip(control, $"Copy the link to the clipboard. Will copy http://localhost:{portNumber}?show{linkType}")
    End Sub

    Public Sub SetupTooltips(form As MainUI)
        ' File Operations
        toolTip.SetToolTip(form.SearchForProgramBTN, "Select the program file.")
        toolTip.SetToolTip(form.CaptionsInputBtn, "Select the program file.")
        toolTip.SetToolTip(form.CaptionsOutputBtn, "Select the program file.")
        toolTip.SetToolTip(form.CookiesRefresh, "Clear the set cookie.")

        ' Audio Source Options
        toolTip.SetToolTip(form.HSL_RadioButton, "Use HLS stream instead of microphone. HLS stream is a stream of audio from a website.")
        toolTip.SetToolTip(form.MIC_RadioButton, "Use microphone instead of HLS stream.")
        toolTip.SetToolTip(form.CAP_RadioButton, "Use microphone instead of HLS stream.")

        ' Processing Options
        toolTip.SetToolTip(form.CUDA_RadioButton, "Use CUDA for speech recognition. More powerful but requires a GPU.")
        toolTip.SetToolTip(form.CPU_RadioButton, "Use CPU for speech recognition. Less powerful but does not require a GPU.")
        
        ' Server Options
        toolTip.SetToolTip(form.WebServerButton, "Enable the web server. This will allow you to view the output of the program in a web browser.")
        
        ' Resource Settings
        toolTip.SetToolTip(form.RamSize, "Set the amount of V-RAM to use for the program. This is in GB. The higher the number the more RAM it will use but the more accurate it will be.")
        toolTip.SetToolTip(form.CookiesName, "Set the cookie to use for the program. This will allow you to use a premium account.")
        
        ' Language Settings
        toolTip.SetToolTip(form.StreamLanguage, "Set the language of the stream. This is the language that the stream is in.")
        toolTip.SetToolTip(form.EnglishTranslationCheckBox, "Enable English translation. This will translate the stream to English.")
        toolTip.SetToolTip(form.SecondaryTranslationLanguage, "Set the language to translate the stream to. This is the language that the stream will be translated to.")
        
        ' Integration Settings
        toolTip.SetToolTip(form.DiscordWebHook, "Set the discord webhook to use. This will send the output of the program to a discord channel.")
        
        ' Stream Settings
        toolTip.SetToolTip(form.HLS_URL, "Set the HLS stream URL to use. This is the URL of the stream. Example: https://example.com/stream")
        toolTip.SetToolTip(form.ChunkSizeTrackBar, "Set the chunk size. This is the amount of audio to process at once. The higher the number the more accurate it will be but the more delay there will be.")
        toolTip.SetToolTip(form.ShowOriginalText, "Show the original text of the stream. This will show the original text of the stream. So if the speaker is speaking Japanese it will show the Japanese text.")
        toolTip.SetToolTip(form.RepeatProtection, "Will help the model from repeating itself, but may slow up the process.")
    End Sub

    Public Sub ShowMicrophoneSettingsHelp(control As String)
        Select Case control
            Case "Energy_Threshold"
                MessageBox.Show("Set the energy threshold. This is the amount of energy required to start recording. The higher the number the more energy is required to start recording.")
            Case "MicCaliLbl"
                MessageBox.Show("Set the microphone calibration time. This is the amount of time to calibrate the microphone. The higher the number the more time it will take to calibrate the microphone.")
            Case "RecordTimeoutLbl"
                MessageBox.Show("Set the record timeout. This is the amount of time to record for. The higher the number the more time it will record for.")
            Case "PhraseTimeOutlbl"
                MessageBox.Show("Set the phrase timeout. This is the amount of time to wait for a phrase. The higher the number the more time it will wait for a phrase. How many sentences in a paragraph it'll show.")
            Case "SetMicLbl"
                MessageBox.Show("Set the microphone to use, click Get IDs and set the ID of the microphone.")
        End Select
    End Sub
End Class