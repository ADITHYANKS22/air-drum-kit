import json
import logging
import cv2

from airdrum.camera import Camera
from airdrum.config import CameraConfig
from airdrum.drum_layout import DrumLayout

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class InteractiveLayoutEditor:
    """Mouse-driven drag-and-drop layout editor for drum pads."""

    def __init__(self, layout_path: str = "assets/layouts/default.json") -> None:
        self.layout_path = layout_path
        self.layout = DrumLayout(layout_path)

        self.selected_pad_idx = -1
        self.is_dragging = False
        self.is_resizing = False
        self.drag_offset_x = 0.0
        self.drag_offset_y = 0.0

    def _get_pad_dims(self, pad):
        w = getattr(pad, "width", getattr(pad, "w", 0.0))
        h = getattr(pad, "height", getattr(pad, "h", 0.0))
        return w, h

    def _set_pad_dims(self, pad, w, h):
        if hasattr(pad, "width"):
            pad.width = w
        if hasattr(pad, "w"):
            pad.w = w
        if hasattr(pad, "height"):
            pad.height = h
        if hasattr(pad, "h"):
            pad.h = h

    def mouse_callback(self, event, x, y, flags, param):
        norm_x = x / param["width"]
        norm_y = y / param["height"]

        if event == cv2.EVENT_LBUTTONDOWN:
            for idx, pad in enumerate(self.layout.pads):
                pad_w, pad_h = self._get_pad_dims(pad)
                br_x = pad.x + pad_w
                br_y = pad.y + pad_h

                if abs(norm_x - br_x) < 0.03 and abs(norm_y - br_y) < 0.03:
                    self.selected_pad_idx = idx
                    self.is_resizing = True
                    return

                if pad.x <= norm_x <= pad.x + pad_w and pad.y <= norm_y <= pad.y + pad_h:
                    self.selected_pad_idx = idx
                    self.is_dragging = True
                    self.drag_offset_x = norm_x - pad.x
                    self.drag_offset_y = norm_y - pad.y
                    return

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.selected_pad_idx >= 0:
                pad = self.layout.pads[self.selected_pad_idx]
                pad_w, pad_h = self._get_pad_dims(pad)

                if self.is_dragging:
                    pad.x = max(0.0, min(1.0 - pad_w, norm_x - self.drag_offset_x))
                    pad.y = max(0.0, min(1.0 - pad_h, norm_y - self.drag_offset_y))
                elif self.is_resizing:
                    new_w = max(0.05, min(1.0 - pad.x, norm_x - pad.x))
                    new_h = max(0.05, min(1.0 - pad.y, norm_y - pad.y))
                    self._set_pad_dims(pad, new_w, new_h)

        elif event == cv2.EVENT_LBUTTONUP:
            self.is_dragging = False
            self.is_resizing = False

    def save_layout(self) -> None:
        """Saves updated pad positions matching DrumLayout's schema."""
        pads_data = []
        for pad in self.layout.pads:
            pad_w, pad_h = self._get_pad_dims(pad)
            pads_data.append(
                {
                    "id": pad.id,
                    "name": pad.name,
                    "x": round(pad.x, 3),
                    "y": round(pad.y, 3),
                    "width": round(pad_w, 3),
                    "height": round(pad_h, 3),
                    "color": pad.color,
                }
            )

        data = {"pads": pads_data}
        with open(self.layout_path, "w") as f:
            json.dump(data, f, indent=4)
        logging.info("Saved updated layout configuration to %s", self.layout_path)

    def run(self) -> None:
        camera = Camera(CameraConfig(width=1280, height=720))
        window_name = "Air Drum Kit - Interactive Layout Editor"
        cv2.namedWindow(window_name)

        frame_dimensions = {"width": 1280, "height": 720}
        cv2.setMouseCallback(window_name, self.mouse_callback, param=frame_dimensions)

        print("\n--- Layout Editor Controls ---")
        print("• Left-Click & Drag Pad: Move pad position")
        print("• Left-Click & Drag Bottom-Right Corner: Resize pad")
        print("• Press 's': Save current layout to JSON")
        print("• Press 'q': Exit editor\n")

        try:
            while True:
                ret, frame = camera.read()
                if not ret or frame is None:
                    continue

                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                frame_dimensions["width"] = w
                frame_dimensions["height"] = h

                annotated = self.layout.draw(frame)

                for idx, pad in enumerate(self.layout.pads):
                    pad_w, pad_h = self._get_pad_dims(pad)
                    px1 = int(pad.x * w)
                    py1 = int(pad.y * h)
                    px2 = int((pad.x + pad_w) * w)
                    py2 = int((pad.y + pad_h) * h)

                    if idx == self.selected_pad_idx:
                        cv2.rectangle(annotated, (px1, py1), (px2, py2), (255, 255, 255), 2)

                    cv2.circle(annotated, (px2, py2), 6, (0, 255, 255), -1)

                cv2.putText(
                    annotated,
                    "LAYOUT EDITOR: Drag inside pad to move | Drag yellow dot to resize | 's' to Save",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2,
                )

                cv2.imshow(window_name, annotated)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("s"):
                    self.save_layout()
                    cv2.putText(
                        annotated,
                        "LAYOUT SAVED!",
                        (w // 2 - 100, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 255, 0),
                        3,
                    )
                    cv2.imshow(window_name, annotated)
                    cv2.waitKey(800)
        finally:
            camera.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    editor = InteractiveLayoutEditor()
    editor.run()