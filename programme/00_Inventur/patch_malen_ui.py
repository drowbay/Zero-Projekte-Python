#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()

OVERLAY_CODE = r'''package com.hucks.canview

import android.app.Service
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.os.IBinder
import android.provider.MediaStore
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.TextView
import android.widget.Toast
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class OverlayService : Service() {
    private lateinit var windowManager: WindowManager
    private lateinit var canView: CanView
    private lateinit var controlPanel: LinearLayout
    private lateinit var brushLabel: TextView
    private lateinit var drawParams: WindowManager.LayoutParams
    private lateinit var panelParams: WindowManager.LayoutParams

    private var drawMode = true

    // Schaltplan/Fenster bewusst kleiner als vorher, Bedienung bleibt gleich.
    private var canvasWidth = 720
    private var canvasHeight = 520

    private val overlayType: Int
        get() = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        createDrawingOverlay()
        createControlPanel()
        Toast.makeText(this, "CanView Overlay gestartet", Toast.LENGTH_SHORT).show()
    }

    private fun createDrawingOverlay() {
        canView = CanView(this).apply {
            setBackgroundColor(android.graphics.Color.TRANSPARENT)
        }

        drawParams = WindowManager.LayoutParams(
            canvasWidth,
            canvasHeight,
            overlayType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            android.graphics.PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 20
            y = 150
        }

        windowManager.addView(canView, drawParams)
    }

    private fun createControlPanel() {
        controlPanel = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(12, 12, 12, 12)
            setBackgroundColor(android.graphics.Color.argb(210, 20, 20, 20))
        }

        val title = TextView(this).apply {
            text = "Zeichenfenster"
            setTextColor(android.graphics.Color.WHITE)
            textSize = 16f
        }
        controlPanel.addView(title)

        brushLabel = TextView(this).apply {
            text = "Pinsel: ${canView.brushSize.toInt()}"
            setTextColor(android.graphics.Color.WHITE)
        }
        controlPanel.addView(brushLabel)

        val seekBar = SeekBar(this).apply {
            max = 40
            progress = canView.brushSize.toInt().coerceAtLeast(1)
            setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    val size = progress.coerceAtLeast(1).toFloat()
                    canView.setBrushSize(size)
                    brushLabel.text = "Pinsel: ${size.toInt()}"
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })
        }
        controlPanel.addView(seekBar)

        val rowOne = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        val rowTwo = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        val rowThree = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }

        val modeButton = Button(this).apply {
            text = "Malen AN"
            setOnClickListener {
                toggleDrawMode()
                text = if (drawMode) "Malen AN" else "Durchklicken AN"
                Toast.makeText(this@OverlayService, if (drawMode) "Malen aktiv" else "Durchklicken aktiv", Toast.LENGTH_SHORT).show()
            }
        }

        val clearButton = Button(this).apply {
            text = "Leeren"
            setOnClickListener { canView.clearCanvas() }
        }

        val biggerButton = Button(this).apply {
            text = "Fenster +"
            setOnClickListener { updateCanvasSize(120) }
        }

        val smallerButton = Button(this).apply {
            text = "Fenster -"
            setOnClickListener { updateCanvasSize(-120) }
        }

        val saveButton = Button(this).apply {
            text = "Speichern"
            setOnClickListener { saveCurrentDrawing() }
        }

        val whiteButton = Button(this).apply {
            text = "Weiß AUS"
            setOnClickListener {
                val enabled = canView.toggleWhiteBackground()
                text = if (enabled) "Weiß AN" else "Weiß AUS"
            }
        }

        val closeButton = Button(this).apply {
            text = "Schließen"
            setOnClickListener { stopSelf() }
        }

        rowOne.addView(modeButton)
        rowOne.addView(clearButton)
        rowTwo.addView(smallerButton)
        rowTwo.addView(biggerButton)
        rowThree.addView(saveButton)
        rowThree.addView(whiteButton)
        rowThree.addView(closeButton)

        controlPanel.addView(rowOne)
        controlPanel.addView(rowTwo)
        controlPanel.addView(rowThree)

        panelParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            overlayType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            android.graphics.PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 20
            y = 20
        }

        windowManager.addView(controlPanel, panelParams)
    }

    private fun toggleDrawMode() {
        drawMode = !drawMode
        drawParams.flags = if (drawMode) {
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
        } else {
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
        }
        windowManager.updateViewLayout(canView, drawParams)
    }

    private fun updateCanvasSize(delta: Int) {
        canvasWidth = (canvasWidth + delta).coerceAtLeast(280)
        canvasHeight = (canvasHeight + delta).coerceAtLeast(220)
        drawParams.width = canvasWidth
        drawParams.height = canvasHeight
        windowManager.updateViewLayout(canView, drawParams)
    }

    private fun saveCurrentDrawing() {
        val bitmap = canView.exportBitmap()
        val fileName = "CanView_${SimpleDateFormat("yyyyMMdd_HHmmss", Locale.GERMANY).format(Date())}.png"

        try {
            val resolver = contentResolver
            val uri: Uri? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val values = ContentValues().apply {
                    put(MediaStore.Images.Media.DISPLAY_NAME, fileName)
                    put(MediaStore.Images.Media.MIME_TYPE, "image/png")
                    put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/CanView")
                    put(MediaStore.Images.Media.IS_PENDING, 1)
                }
                resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)?.also { imageUri ->
                    resolver.openOutputStream(imageUri)?.use { out ->
                        bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
                    }
                    val doneValues = ContentValues().apply {
                        put(MediaStore.Images.Media.IS_PENDING, 0)
                    }
                    resolver.update(imageUri, doneValues, null, null)
                }
            } else {
                @Suppress("DEPRECATION")
                val values = ContentValues().apply {
                    put(MediaStore.Images.Media.DISPLAY_NAME, fileName)
                    put(MediaStore.Images.Media.MIME_TYPE, "image/png")
                }
                @Suppress("DEPRECATION")
                resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)?.also { imageUri ->
                    resolver.openOutputStream(imageUri)?.use { out ->
                        bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
                    }
                }
            }

            Toast.makeText(this, if (uri != null) "Gespeichert" else "Speichern fehlgeschlagen", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Speichern fehlgeschlagen: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::canView.isInitialized) windowManager.removeView(canView)
        if (::controlPanel.isInitialized) windowManager.removeView(controlPanel)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
'''

CANVIEW_CODE = r'''package com.hucks.canview

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View

class CanView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    data class Stroke(val path: Path, val color: Int, val size: Float)

    private val strokes = ArrayList<Stroke>()
    private var currentPath: Path? = null
    private var whiteBackground = false

    var brushSize: Float = 6f
        private set

    var brushColor: Int = Color.RED
        private set

    private val paint = Paint().apply {
        isAntiAlias = true
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
        strokeWidth = brushSize
        color = brushColor
    }

    fun setBrushSize(size: Float) {
        brushSize = size.coerceAtLeast(1f)
        paint.strokeWidth = brushSize
    }

    fun setBrushColor(color: Int) {
        brushColor = color
        paint.color = brushColor
    }

    fun toggleWhiteBackground(): Boolean {
        whiteBackground = !whiteBackground
        invalidate()
        return whiteBackground
    }

    fun clearCanvas() {
        strokes.clear()
        currentPath = null
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        if (whiteBackground) {
            canvas.drawColor(Color.WHITE)
        }

        for (stroke in strokes) {
            paint.color = stroke.color
            paint.strokeWidth = stroke.size
            canvas.drawPath(stroke.path, paint)
        }

        currentPath?.let {
            paint.color = brushColor
            paint.strokeWidth = brushSize
            canvas.drawPath(it, paint)
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val x = event.x
        val y = event.y

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                currentPath = Path().apply { moveTo(x, y) }
                invalidate()
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                currentPath?.lineTo(x, y)
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP -> {
                currentPath?.let { path ->
                    strokes.add(Stroke(Path(path), brushColor, brushSize))
                }
                currentPath = null
                invalidate()
                return true
            }
        }
        return true
    }

    fun exportBitmap(): Bitmap {
        val bitmap = Bitmap.createBitmap(width.coerceAtLeast(1), height.coerceAtLeast(1), Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        if (whiteBackground) {
            canvas.drawColor(Color.WHITE)
        }
        draw(canvas)
        return bitmap
    }
}
'''


def find_file(name: str) -> Path:
    matches = list(ROOT.rglob(name))
    matches = [m for m in matches if "build" not in m.parts]
    if not matches:
        raise SystemExit(f"❌ {name} nicht gefunden. Starte das Script im Android-Studio-Projektordner.")
    return matches[0]


def backup_and_write(path: Path, content: str):
    backup = path.with_suffix(path.suffix + ".zero_backup")
    if not backup.exists():
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(content, encoding="utf-8")
    print(f"✅ gepatcht: {path}")
    print(f"   Backup: {backup}")


def main():
    overlay = find_file("OverlayService.kt")
    canview = find_file("CanView.kt")
    backup_and_write(overlay, OVERLAY_CODE)
    backup_and_write(canview, CANVIEW_CODE)
    print("\nFertig. Danach in Android Studio: Build > Build APK(s)")
    print("Oder im Terminal: ./gradlew assembleDebug")

if __name__ == "__main__":
    main()
