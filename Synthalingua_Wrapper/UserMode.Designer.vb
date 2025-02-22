<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class UserMode
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(UserMode))
        Label1 = New Label()
        AdvBtn = New Button()
        SimpleBtn = New Button()
        SuspendLayout()
        ' 
        ' Label1
        ' 
        Label1.Dock = DockStyle.Top
        Label1.Font = New Font("Segoe UI", 19F)
        Label1.Location = New Point(0, 0)
        Label1.Name = "Label1"
        Label1.Size = New Size(1139, 421)
        Label1.TabIndex = 0
        Label1.Text = resources.GetString("Label1.Text")
        ' 
        ' AdvBtn
        ' 
        AdvBtn.Font = New Font("Segoe UI", 24F)
        AdvBtn.Location = New Point(787, 473)
        AdvBtn.Name = "AdvBtn"
        AdvBtn.Size = New Size(340, 85)
        AdvBtn.TabIndex = 1
        AdvBtn.Text = "Start Advanced Mode"
        AdvBtn.UseVisualStyleBackColor = True
        ' 
        ' SimpleBtn
        ' 
        SimpleBtn.Font = New Font("Segoe UI", 24F)
        SimpleBtn.Location = New Point(12, 473)
        SimpleBtn.Name = "SimpleBtn"
        SimpleBtn.Size = New Size(340, 85)
        SimpleBtn.TabIndex = 2
        SimpleBtn.Text = "Start Basic Mode"
        SimpleBtn.UseVisualStyleBackColor = True
        ' 
        ' UserMode
        ' 
        AutoScaleDimensions = New SizeF(7F, 15F)
        AutoScaleMode = AutoScaleMode.Font
        ClientSize = New Size(1139, 570)
        Controls.Add(SimpleBtn)
        Controls.Add(AdvBtn)
        Controls.Add(Label1)
        FormBorderStyle = FormBorderStyle.Fixed3D
        MaximizeBox = False
        Name = "UserMode"
        StartPosition = FormStartPosition.CenterScreen
        Text = "Main - User Mode"
        ResumeLayout(False)
    End Sub

    Friend WithEvents Label1 As Label
    Friend WithEvents AdvBtn As Button
    Friend WithEvents SimpleBtn As Button
End Class
