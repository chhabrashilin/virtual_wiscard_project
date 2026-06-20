// jsbarcode does not ship TypeScript definitions, and pulling in @types/jsbarcode
// would require a package-lock change. This minimal declaration is enough for our
// usage (rendering a CODE128 barcode into an <svg> element).
declare module 'jsbarcode' {
  interface JsBarcodeOptions {
    format?: string
    width?: number
    height?: number
    displayValue?: boolean
    fontSize?: number
    margin?: number
    background?: string
    lineColor?: string
    text?: string
    [key: string]: unknown
  }

  function JsBarcode(
    element: Element | string | null,
    data: string,
    options?: JsBarcodeOptions
  ): void

  export default JsBarcode
}
