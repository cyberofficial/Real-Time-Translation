Imports System.IO

Public Class ConfigManager
    Public Shared Function SaveConfig(settings As MainUI) As Boolean
        Try
            With My.Settings
                ' Script Location
                .MainScriptLocation = settings.ScriptFileLocation.Text

                ' Audio Source
                .AudioSource = If(settings.HSL_RadioButton.Checked, 1, If(settings.MIC_RadioButton.Checked, 2, 3))

                ' Processor Device
                .ProcDevice = If(settings.CUDA_RadioButton.Checked, 1, 2)

                ' Web Server
                .WebServerEnabled = If(settings.WebServerButton.Checked, 1, 0)
                .WebServerPort = settings.PortNumber.Value

                ' RAM Size
                .RamSize = settings.RamSize.Text

                ' Model Location
                .modelDIr = settings.modelDIr.Text

                ' Force RAM
                .ForceRam = settings.ForceRam.Checked

                ' Cookie Name
                .CookieName = settings.CookiesName.Text

                ' Stream Language
                .StreamLanguage = settings.StreamLanguage.Text

                ' English Translation
                .EnglishTranslationEnabled = settings.EnglishTranslationCheckBox.Checked

                ' Secondary Translation
                .SecondaryTranslationLang = settings.SecondaryTranslationLanguage.Text
                .SecondaryTranslationEnabled = settings.SecondaryTranslation.Checked

                ' HLS URL
                .HLSurl = settings.HLS_URL.Text

                ' Stream Chunk Size
                .StreamChunkSize = settings.ChunkSizeTrackBar.Value

                ' Show Original Text
                .HLSShowOriginal = settings.ShowOriginalText.Checked

                ' Microphone Energy Threshold
                .MicrophoneEnergyThreshold = settings.EnThreshValue.Value
                .MicrophoneEnergyThresholdEnabled = settings.MicEnCheckBox.Checked

                ' Microphone Calibration Time
                .MicCalTime = settings.MicCaliTime.Value
                .MicCalTImeEnabled = settings.MicCaliCheckBox.Checked

                ' Microphone Record Timeout
                .MicRecTimeout = settings.RecordTimeout.Value
                .MicRecTimeoutEnabled = settings.RecordTimeOutCHeckBox.Checked

                ' Phrase Timeout
                .PhraseTimeOut = settings.PhraseTimeout.Value
                .PhraseTimeOutEnabled = settings.PhraseTimeOutCheckbox.Checked

                ' Word Block List
                .WordBlockListEnabled = settings.WordBlockList.Checked
                .WordBlockListLocation = settings.WordBlockListLocation.ToString

                ' Repeat Protection
                .RepeatProtection = settings.RepeatProtection.Checked

                ' Command Block
                .PrimaryFolder = settings.PrimaryFolder
                .ShortCutType = settings.ShortCutType
                .CommandBlock = settings.ConfigTextBox.Text

                'hls info
                .hlspassid = settings.hlspassid.Text
                .hlspassword = settings.hlspassword.Text
                .cb_halspassword = settings.cb_halspassword.Checked

                'Precision Mode
                .fp16 = settings.PrecisionCheckBox.Checked
            End With
            My.Settings.Save()
            Return True
        Catch ex As Exception
            Return False
        End Try
    End Function

    Public Shared Function LoadConfig(form As MainUI) As Boolean
        Try
            With My.Settings
                If String.IsNullOrEmpty(.MainScriptLocation) Then
                    ' No script location set yet
                Else
                    form.ScriptFileLocation.Text = .MainScriptLocation
                End If

                form.HSL_RadioButton.Checked = (.AudioSource = 1)
                form.MIC_RadioButton.Checked = (.AudioSource = 2)
                form.CAP_RadioButton.Checked = (.AudioSource = 3)

                form.CUDA_RadioButton.Checked = (.ProcDevice = 1)
                form.CPU_RadioButton.Checked = Not (.ProcDevice = 1)

                form.PortNumber.Value = .WebServerPort
                form.WebServerButton.Checked = .WebServerEnabled
                form.RamSize.Text = .RamSize
                form.ForceRam.Checked = .ForceRam
                form.CookiesName.Text = .CookieName
                form.StreamLanguage.Text = .StreamLanguage
                form.EnglishTranslationCheckBox.Checked = .EnglishTranslationEnabled
                form.SecondaryTranslationLanguage.Text = .SecondaryTranslationLang
                form.SecondaryTranslation.Checked = .SecondaryTranslationEnabled
                form.HLS_URL.Text = .HLSurl
                form.ChunkSizeTrackBar.Value = .StreamChunkSize
                form.ShowOriginalText.Checked = .HLSShowOriginal
                form.EnThreshValue.Value = .MicrophoneEnergyThreshold
                form.MicEnCheckBox.Checked = .MicrophoneEnergyThresholdEnabled
                form.MicCaliTime.Value = .MicCalTime
                form.MicCaliCheckBox.Checked = .MicCalTImeEnabled
                form.RecordTimeout.Value = .MicRecTimeout
                form.RecordTimeOutCHeckBox.Checked = .MicRecTimeoutEnabled
                form.PhraseTimeout.Value = .PhraseTimeOut
                form.PhraseTimeOutCheckbox.Checked = .PhraseTimeOutEnabled
                form.WordBlockListLocation = .WordBlockListLocation
                form.WordBlockList.Checked = .WordBlockListEnabled
                form.RepeatProtection.Checked = .RepeatProtection
                form.ConfigTextBox.Text = .CommandBlock
                form.ShortCutType = .ShortCutType
                form.hlspassid.Text = .hlspassid
                form.hlspassword.Text = .hlspassword
                form.cb_halspassword.Checked = .cb_halspassword
                form.modelDIr.Text = .modelDIr
                form.PrecisionCheckBox.Checked = .fp16

                Try
                    form.PrimaryFolder = .PrimaryFolder
                Catch ex As Exception
                    form.PrimaryFolder = ""
                End Try
            End With
            Return True
        Catch ex As Exception
            Return False
        End Try
    End Function
End Class