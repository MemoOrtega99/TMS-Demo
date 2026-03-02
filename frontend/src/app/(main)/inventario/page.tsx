"use client"

import { useState } from "react"
import { Search, Plus, Package, TrendingDown, AlertTriangle } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface InventoryItem {
    id: number
    codigo: string
    nombre: string
    categoria: string
    stock_actual: number
    stock_minimo: number
    unidad_medida: string
    precio_promedio: number
    ubicacion: string
}

const MOCK_INVENTORY: InventoryItem[] = [
    { id: 1, codigo: "REF-001", nombre: "Filtro de aceite motor (Freightliner)", categoria: "REFACCIONES", stock_actual: 2, stock_minimo: 5, unidad_medida: "pza", precio_promedio: 850, ubicacion: "Estante A1" },
    { id: 2, codigo: "LLA-001", nombre: "Llanta 11R22.5 (Bridgestone)", categoria: "LLANTAS", stock_actual: 8, stock_minimo: 4, unidad_medida: "pza", precio_promedio: 6800, ubicacion: "Bodega principal" },
    { id: 3, codigo: "LUB-001", nombre: "Aceite motor Mobil 15W-40 (Caneca 19L)", categoria: "LUBRICANTES", stock_actual: 12, stock_minimo: 6, unidad_medida: "pza", precio_promedio: 1250, ubicacion: "Estante B2" },
    { id: 4, codigo: "REF-002", nombre: "Filtro de combustible Kenworth", categoria: "REFACCIONES", stock_actual: 4, stock_minimo: 5, unidad_medida: "pza", precio_promedio: 420, ubicacion: "Estante A2" },
    { id: 5, codigo: "LLA-002", nombre: "Llanta de repuesto 315/80R22.5", categoria: "LLANTAS", stock_actual: 3, stock_minimo: 2, unidad_medida: "pza", precio_promedio: 7200, ubicacion: "Bodega principal" },
    { id: 6, codigo: "REF-003", nombre: "Pastillas de freno traseras", categoria: "REFACCIONES", stock_actual: 6, stock_minimo: 4, unidad_medida: "jgo", precio_promedio: 1800, ubicacion: "Estante A3" },
    { id: 7, codigo: "LUB-002", nombre: "Líquido de frenos DOT4 (1L)", categoria: "LUBRICANTES", stock_actual: 15, stock_minimo: 8, unidad_medida: "pza", precio_promedio: 165, ubicacion: "Estante B1" },
    { id: 8, codigo: "HER-001", nombre: "Gato hidráulico 20T", categoria: "HERRAMIENTAS", stock_actual: 2, stock_minimo: 1, unidad_medida: "pza", precio_promedio: 4500, ubicacion: "Herramientas" },
    { id: 9, codigo: "REF-004", nombre: "Banda de distribución Freightliner", categoria: "REFACCIONES", stock_actual: 1, stock_minimo: 3, unidad_medida: "pza", precio_promedio: 2800, ubicacion: "Estante A4" },
    { id: 10, codigo: "LUB-003", nombre: "Grasa de chasis (Bote 400g)", categoria: "LUBRICANTES", stock_actual: 20, stock_minimo: 10, unidad_medida: "pza", precio_promedio: 98, ubicacion: "Estante B3" },
]

const categoriaColor: Record<string, string> = {
    REFACCIONES: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    LLANTAS: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    LUBRICANTES: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    HERRAMIENTAS: "bg-violet-500/15 text-violet-400 border-violet-500/30",
    COMBUSTIBLE: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

export default function InventarioPage() {
    const [search, setSearch] = useState("")
    const [filterLow, setFilterLow] = useState(false)

    const itemsLow = MOCK_INVENTORY.filter(i => i.stock_actual < i.stock_minimo)
    const valorTotal = MOCK_INVENTORY.reduce((a, i) => a + i.stock_actual * i.precio_promedio, 0)

    const filtered = MOCK_INVENTORY.filter(i => {
        const matchSearch = !search || [i.codigo, i.nombre, i.categoria, i.ubicacion].some(f => f.toLowerCase().includes(search.toLowerCase()))
        const matchLow = !filterLow || i.stock_actual < i.stock_minimo
        return matchSearch && matchLow
    })

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Inventario</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Inventario</h1>
                </div>
                <button className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nuevo artículo
                </button>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{MOCK_INVENTORY.length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Artículos registrados</div>
                </CardContent></Card>
                <Card className={itemsLow.length > 0 ? "border-destructive/40" : ""}><CardContent className="pt-4 pb-4 px-4">
                    <div className={`text-xl font-bold flex items-center gap-2 ${itemsLow.length > 0 ? "text-destructive" : ""}`}>
                        {itemsLow.length > 0 && <AlertTriangle className="h-4 w-4" />}
                        {itemsLow.length}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">Stock bajo mínimo</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums">{MXN(valorTotal)}</div>
                    <div className="text-xs text-muted-foreground mt-1">Valor total inventario</div>
                </CardContent></Card>
            </div>

            <div className="flex gap-3">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input type="text" placeholder="Buscar por código, nombre, categoría..." value={search} onChange={e => setSearch(e.target.value)}
                        className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
                </div>
                <button onClick={() => setFilterLow(!filterLow)}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-md text-sm border transition-colors ${filterLow ? "bg-destructive/15 text-destructive border-destructive/30" : "border-input text-muted-foreground hover:text-foreground"}`}>
                    <TrendingDown className="h-4 w-4" />
                    Stock bajo
                </button>
            </div>

            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["Código", "Artículo", "Categoría", "Stock", "Mínimo", "Estado", "Precio prom.", "Ubicación"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filtered.map(item => {
                                const isLow = item.stock_actual < item.stock_minimo
                                return (
                                    <tr key={item.id} className={`hover:bg-muted/30 transition-colors ${isLow ? "bg-destructive/5" : ""}`}>
                                        <td className="px-5 py-3.5 font-mono text-xs font-medium">{item.codigo}</td>
                                        <td className="px-4 py-3.5 text-xs font-medium max-w-[220px]">{item.nombre}</td>
                                        <td className="px-4 py-3.5">
                                            <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${categoriaColor[item.categoria] ?? "bg-muted text-muted-foreground border-border"}`}>
                                                {item.categoria.charAt(0) + item.categoria.slice(1).toLowerCase()}
                                            </span>
                                        </td>
                                        <td className={`px-4 py-3.5 text-sm font-bold tabular-nums ${isLow ? "text-destructive" : ""}`}>
                                            {item.stock_actual} {item.unidad_medida}
                                        </td>
                                        <td className="px-4 py-3.5 text-xs text-muted-foreground tabular-nums">{item.stock_minimo} {item.unidad_medida}</td>
                                        <td className="px-4 py-3.5">
                                            {isLow
                                                ? <span className="inline-flex items-center gap-1 text-xs text-destructive"><AlertTriangle className="h-3 w-3" />Bajo mínimo</span>
                                                : <span className="text-xs text-emerald-400">Normal</span>
                                            }
                                        </td>
                                        <td className="px-4 py-3.5 text-xs tabular-nums text-muted-foreground">{MXN(item.precio_promedio)}</td>
                                        <td className="px-4 pr-5 py-3.5 text-xs text-muted-foreground">{item.ubicacion}</td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
