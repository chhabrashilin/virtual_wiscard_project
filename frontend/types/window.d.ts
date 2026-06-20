// Type definitions for window.ethereum (MetaMask)
interface Window {
  ethereum?: {
    isMetaMask?: boolean;
    request: (args: { method: string; params?: Array<any> }) => Promise<any>;
    on?: (event: string, callback: (...args: any[]) => void) => void;
    removeListener?: (event: string, callback: (...args: any[]) => void) => void;
    selectedAddress?: string | null;
  };
  BarcodeDetector?: BarcodeDetectorConstructor;
}

// Minimal typings for the browser BarcodeDetector API (Chromium).
interface DetectedBarcode {
  rawValue: string;
  format: string;
}

interface BarcodeDetectorConstructor {
  new (options?: { formats?: string[] }): {
    detect: (source: CanvasImageSource) => Promise<DetectedBarcode[]>;
  };
  getSupportedFormats?: () => Promise<string[]>;
}

declare const BarcodeDetector: BarcodeDetectorConstructor | undefined;
