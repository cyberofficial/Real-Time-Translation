Imports System.Text
Imports System.IO

Public Class CommandGenerator
    Private ReadOnly builder As StringBuilder
    Private ReadOnly settings As MainUI

    Public Sub New(mainForm As MainUI)
        builder = New StringBuilder()
        settings = mainForm
    End Sub

    Public Function Generate() As String
        If String.IsNullOrEmpty(settings.ScriptFileLocation.Text) Then
            Throw New Exception("Please select the program file.")
        End If
        If String.IsNullOrEmpty(settings.StreamLanguage.Text) Then
            Throw New Exception("No Stream language was set.")
        End If

        settings.ShortCutType = If(settings.ScriptFileLocation.Text.Contains("transcribe_audio.py"), "Source", "Portable")
        settings.PrimaryFolder = Path.GetDirectoryName(settings.ScriptFileLocation.Text)

        ' Basic setup
        builder.Clear()
        builder.AppendLine().AppendLine("cls").AppendLine("@echo off").AppendLine("Echo Loading Script")
        builder.AppendLine($"""{settings.PrimaryFolder}\set_up_env.exe""")
        builder.AppendLine($"call ""{settings.PrimaryFolder}\ffmpeg_path.bat""")

        ' Script execution command
        If settings.ShortCutType = "Source" Then
            builder.AppendLine($"call ""{settings.PrimaryFolder}\data_whisper\Scripts\activate.bat""")
            builder.Append($"python ""{settings.PrimaryFolder}\transcribe_audio.py"" ")
        Else
            builder.Append($"""{settings.PrimaryFolder}\transcribe_audio.exe"" ")
        End If

        AppendRamSettings()
        AppendAudioSourceSettings()
        AppendLanguageSettings()
        AppendDeviceSettings()
        AppendAdditionalSettings()

        builder.AppendLine().AppendLine("pause")
        Return builder.ToString()
    End Function

    Private Sub AppendRamSettings()
        builder.Append($"--ram {settings.RamSize.Text} ")
        If settings.ForceRam.Checked Then builder.Append("--ramforce ")
    End Sub

    Private Sub AppendAudioSourceSettings()
        If settings.CAP_RadioButton.Checked Then
            builder.Append($"--makecaptions --file_input=""{settings.CaptionsInput.Text}"" --file_output=""{settings.CaptionsOutput.Text}"" --file_output_name=""{settings.CaptionsName.Text}"" ")
        ElseIf settings.MIC_RadioButton.Checked Then
            builder.Append("--microphone_enabled true ")
            If settings.MicEnCheckBox.Checked Then builder.Append($"--energy_threshold {settings.EnThreshValue.Value} ")
            If settings.MicCaliCheckBox.Checked Then builder.Append($"--mic_calibration_time {settings.MicCaliTime.Value} ")
            If settings.RecordTimeOutCHeckBox.Checked Then builder.Append($"--record_timeout {settings.RecordTimeout.Value} ")
            If settings.PhraseTimeOutCheckbox.Checked Then builder.Append($"--phrase_timeout {settings.PhraseTimeout.Value} ")
            builder.Append($"--set_microphone {settings.MicID.Value} ")
        ElseIf settings.HSL_RadioButton.Checked Then
            If settings.ShowOriginalText.Checked Then builder.Append("--stream_original_text ")
            builder.Append($"--stream ""{settings.HLS_URL.Text}"" ")
            builder.Append($"--stream_chunks {settings.ChunkSizeTrackBar.Value} ")
        End If
    End Sub

    Private Sub AppendLanguageSettings()
        Dim prefix = If(settings.HSL_RadioButton.Checked, "stream_", "")
        If settings.StreamLanguage.Text <> "--Auto Detect--" Then
            builder.Append($"--{prefix}language {settings.StreamLanguage.Text} ")
        End If

        If settings.EnglishTranslationCheckBox.Checked Then
            builder.Append($"--{prefix}translate ")
        End If
        If settings.SecondaryTranslation.Checked Then
            builder.Append($"--{prefix}transcribe ")
            builder.Append($"--{prefix}target_language {settings.SecondaryTranslationLanguage.Text} ")
        End If
    End Sub

    Private Sub AppendDeviceSettings()
        If settings.CUDA_RadioButton.Checked Then
            builder.Append("--device cuda ")
        ElseIf settings.CPU_RadioButton.Checked Then
            builder.Append("--device cpu ")
        End If
    End Sub

    Private Sub AppendAdditionalSettings()
        If Not String.IsNullOrEmpty(settings.CookiesName.Text) Then builder.Append($"--cookies {settings.CookiesName.Text} ")
        If settings.WordBlockList.Checked Then builder.Append($"--ignorelist ""{settings.WordBlockListLocation}"" ")
        If settings.WebServerButton.Checked Then builder.Append($"--portnumber {settings.PortNumber.Value} ")
        If settings.RepeatProtection.Checked Then builder.Append("--condition_on_previous_text ")
        If settings.cb_halspassword.Checked Then builder.Append($"--remote_hls_password_id {settings.hlspassid.Text} --remote_hls_password {settings.hlspassword.Text} ")
        If Not String.IsNullOrEmpty(settings.DiscordWebHook.Text) Then builder.Append($"--discord_webhook ""{settings.DiscordWebHook.Text}"" ")
        If Not String.IsNullOrEmpty(settings.modelDIr.Text) Then builder.Append($"--model_dir ""{settings.modelDIr.Text}"" ")
        If settings.PrecisionCheckBox.Checked Then builder.Append("--fp16")
    End Sub
End Class