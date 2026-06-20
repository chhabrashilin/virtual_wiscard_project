'use client'

import { useEffect, useRef } from 'react'
import JsBarcode from 'jsbarcode'

interface BarcodeProps {
  value: string
  height?: number
}

/**
 * Renders a scannable CODE128 barcode of the student ID. (Note: jsbarcode does
 * not support PDF417; CODE128 is widely scannable and sufficient for the card
 * front. The binary/PDF417 representation lives in the wallet-pass payload.)
 */
export default function Barcode({ value, height = 60 }: BarcodeProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || !value) return
    try {
      JsBarcode(svgRef.current, value, {
        format: 'CODE128',
        height,
        displayValue: true,
        fontSize: 14,
        margin: 8,
        background: '#ffffff',
        lineColor: '#111111',
      })
    } catch (err) {
      console.error('Failed to render barcode:', err)
    }
  }, [value, height])

  return <svg ref={svgRef} className="w-full max-w-xs" />
}
