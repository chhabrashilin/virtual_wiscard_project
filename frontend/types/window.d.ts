// Type definitions for window.ethereum (MetaMask)
interface Window {
  ethereum?: {
    isMetaMask?: boolean;
    request: (args: { method: string; params?: Array<any> }) => Promise<any>;
    on?: (event: string, callback: (...args: any[]) => void) => void;
    removeListener?: (event: string, callback: (...args: any[]) => void) => void;
    selectedAddress?: string | null;
  };
}
