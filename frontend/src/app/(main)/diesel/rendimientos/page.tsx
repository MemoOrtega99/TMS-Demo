"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const RENDIMIENTO_DATA = [
    { unidad: "ECO-001", marca: "Kenworth T680", km_recorridos: 8240, litros_consumidos: 3433, rendimiento: 2.40, eficiencia: "Óptimo" },
    { unidad: "ECO-002", marca: "Freightliner Cascadia", km_recorridos: 12100, litros_consumidos: 5500, rendimiento: 2.20, eficiencia: "Normal" },
    { unidad: "ECO-003", marca: "Kenworth T680 2023", km_recorridos: 3800, litros_consumidos: 2111, rendimiento: 1.80, eficiencia: "Bajo" },
    { unidad: "ECO-004", marca: "International LT", km_recorridos: 6500, litros_consumidos: 2955, rendimiento: 2.20, eficiencia: "Normal" },
    { unidad: "ECO-005", marca: "Peterbilt 389", km_recorridos: 9200, litros_consumidos: 4182, rendimiento: 2.20, eficiencia: "Normal" },
    { unidad: "ECO-006", marca: "Freightliner Cascadia", km_recorridos: 7500, litros_consumidos: 3261, rendimiento: 2.30, eficiencia: "Normal" },
]

const eficienciaColor: Record<string, string> = {
    "Óptimo": "text-emerald-400",
    "Normal": "text-blue-400",
    "Bajo": "text-destructive",
}

const eficienciaBadge: Record<string, string> = {
    "Óptimo": "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    "Normal": "bg-blue-500/15 text-blue-400 border-blue-500/30",
    "Bajo": "bg-red-500/15 text-red-400 border-red-500/30",
}

const NUM = (v: number) => new Intl.NumberFormat("es-MX").format(v)

export default function DieselRendimientosPage() {
    const promedio = (RENDIMIENTO_DATA.reduce((a, r) => a + r.rendimiento, 0) / RENDIMIENTO_DATA.length).toFixed(2)
    const mejor = RENDIMIENTO_DATA.reduce((a, r) => r.rendimiento > a.rendimiento ? r : a)
    const peor = RENDIMIENTO_DATA.reduce((a, r) => r.rendimiento < a.rendimiento ? r : a)

    return (
        <div className="space-y-6">
            <div>
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Diesel</p>
                <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Rendimientos de Flota</h1>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums">{promedio} km/L</div>
                    <div className="text-xs text-muted-foreground mt-1">Promedio de flota</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums text-emerald-400">{mejor.rendimiento} km/L</div>
                    <div className="text-xs text-muted-foreground mt-1">Mejor — {mejor.unidad}</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums text-destructive">{peor.rendimiento} km/L</div>
                    <div className="text-xs text-muted-foreground mt-1">Bajo — {peor.unidad} (revisar)</div>
                </CardContent></Card>
            </div>

            {/* Chart */}
            <Card>
                <CardHeader className="px-5 pt-5 pb-3">
                    <CardTitle className="text-sm font-medium">Rendimiento por unidad (km/L)</CardTitle>
                </CardHeader>
                <CardContent className="px-5 pb-5">
                    <ResponsiveContainer width="100%" height={220}>
                        <BarChart data={RENDIMIENTO_DATA} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                            <XAxis dataKey="unidad" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
                            <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} domain={[0, 3]} />
                            <Tooltip
                                contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px" }}
                                labelStyle={{ color: "hsl(var(--foreground))", fontSize: 12 }}
                                formatter={(value: number) => [`${value} km/L`, "Rendimiento"]}
                            />
                            <Bar dataKey="rendimiento" fill="hsl(var(--foreground))" radius={[4, 4, 0, 0]} maxBarSize={48} />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Detail table */}
            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["Unidad", "Marca / Modelo", "km Recorridos", "Litros consum.", "km/L", "Eficiencia"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {RENDIMIENTO_DATA.map(r => (
                                <tr key={r.unidad} className="hover:bg-muted/30 transition-colors">
                                    <td className="px-5 py-3.5 font-mono text-xs font-semibold">{r.unidad}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{r.marca}</td>
                                    <td className="px-4 py-3.5 text-xs tabular-nums">{NUM(r.km_recorridos)} km</td>
                                    <td className="px-4 py-3.5 text-xs tabular-nums">{NUM(r.litros_consumidos)} L</td>
                                    <td className={`px-4 py-3.5 text-sm font-bold tabular-nums ${eficienciaColor[r.eficiencia]}`}>{r.rendimiento}</td>
                                    <td className="px-4 pr-5 py-3.5">
                                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${eficienciaBadge[r.eficiencia]}`}>
                                            {r.eficiencia}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
