Imports System.IO

Public Class FileOperations
    Public Class ScriptFileInfo
        Public Property ScriptPath As String
        Public Property FolderPath As String
        Public Property ShortcutType As String

        Public Sub New(scriptPath As String, folderPath As String, shortcutType As String)
            Me.ScriptPath = scriptPath
            Me.FolderPath = folderPath
            Me.ShortcutType = shortcutType
        End Sub
    End Class

    Public Shared Function InitializeCookiesFolder(currentDirectory As String) As Boolean
        Try
            Dim cookiesFolderPath As String = Path.Combine(currentDirectory, "cookies")
            If Not Directory.Exists(cookiesFolderPath) Then
                Directory.CreateDirectory(cookiesFolderPath)
            End If
            Return True
        Catch ex As Exception
            Return False
        End Try
    End Function

    Public Shared Function RefreshCookiesList(cookiesComboBox As ComboBox) As Boolean
        Try
            cookiesComboBox.Items.Clear()
            Dim cookiesFolderPath As String = Path.Combine(Application.StartupPath, "cookies")
            If Directory.Exists(cookiesFolderPath) Then
                For Each file As String In Directory.GetFiles(cookiesFolderPath)
                    cookiesComboBox.Items.Add(Path.GetFileNameWithoutExtension(file))
                Next
            End If
            Return True
        Catch ex As Exception
            Return False
        End Try
    End Function

    Public Shared Function FindScriptFile(currentDirectory As String) As ScriptFileInfo
        Dim scriptFilePath As String = Path.Combine(currentDirectory, "transcribe_audio.exe")
        If File.Exists(scriptFilePath) Then
            Return New ScriptFileInfo(scriptFilePath, Path.GetDirectoryName(scriptFilePath), "Portable")
        End If

        scriptFilePath = Path.Combine(currentDirectory, "transcribe_audio.py")
        If File.Exists(scriptFilePath) Then
            Return New ScriptFileInfo(scriptFilePath, Path.GetDirectoryName(scriptFilePath), "Source")
        End If

        Return New ScriptFileInfo(String.Empty, String.Empty, String.Empty)
    End Function

    Public Shared Sub EditWordBlockList(scriptLocation As String, wordBlockListLocation As String)
        Try
            If Not File.Exists(wordBlockListLocation) Then
                Try
                    File.Create(wordBlockListLocation).Close()
                Catch ex As Exception
                    MessageBox.Show("An error occurred while creating the file: " & ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
                    Exit Sub
                End Try
            End If

            Try
                Process.Start("notepad.exe", wordBlockListLocation)
            Catch ex As Exception
                MessageBox.Show("An error occurred while opening the file: " & ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
            End Try
        Catch ex As Exception
            MessageBox.Show(ex.ToString)
        End Try
    End Sub
End Class