import { useRef } from "react";
import { BrowserBarcodeReader } from "@zxing/browser";

export default function Production() {
  const videoRef = useRef(null);
  const inputRef = useRef(null);

  const startScanner = async () => {
    const codeReader = new BrowserBarcodeReader();
    const devices = await BrowserBarcodeReader.listVideoInputDevices();
    const selectedDeviceId = devices[0]?.deviceId;
    if (!selectedDeviceId) {
      alert("No camera found");
      return;
    }
    codeReader.decodeFromVideoDevice(
      selectedDeviceId,
      videoRef.current,
      (result, err) => {
        if (result) {
          inputRef.current.value = result.text;
          codeReader.reset();
        }
      }
    );
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Production Bundle Scanner</h1>
      <button onClick={startScanner}>Scan Bundle</button>
      <div style={{ margin: '20px 0' }}>
        <video ref={videoRef} style={{ width: 300, height: 200 }} />
      </div>
      <input ref={inputRef} id="bundle" placeholder="Scanned Bundle Code" />
    </div>
  );
}
