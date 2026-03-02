"use client"

import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { ArrowUpRight, ArrowDownRight, Activity, Wallet, Truck, TrendingUp, AlertTriangle } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function DashboardPage() {
    const kpis = [
        {
            title: "Facturación del Mes",
            value: "$1,245,000",
            change: "+12.5%",
            trend: "up",
            icon: Wallet,
        },
        {
            title: "Viajes Activos",
            value: "14",
            change: "+2 este mes",
            trend: "up",
            icon: Truck,
        },
        {
            title: "Rentabilidad Promedio",
            value: "32.4%",
            change: "-1.2% vs mes anterior",
            trend: "down",
            icon: Activity,
        },
        {
            title: "CxC Vencidas",
            value: "$345,000",
            change: "3 facturas críticas",
            trend: "alert",
            icon: AlertTriangle,
        },
    ]

    const chartData = [
        { mes: "Sep", ingresos: 850000, gastos: 450000 },
        { mes: "Oct", ingresos: 920000, gastos: 480000 },
        { mes: "Nov", ingresos: 1100000, gastos: 520000 },
        { mes: "Dic", ingresos: 1050000, gastos: 580000 },
        { mes: "Ene", ingresos: 1150000, gastos: 610000 },
        { mes: "Feb", ingresos: 1245000, gastos: 640000 },
    ]

    const recentTrips = [
        { numero: "VJ-2026-0018", origen: "Altamira", destino: "Monterrey", estatus: "en_ruta", unidad: "ECO-003", operador: "J. Martínez" },
        { numero: "VJ-2026-0017", origen: "Tampico", destino: "CDMX", estatus: "en_ruta", unidad: "ECO-005", operador: "R. González" },
        { numero: "VJ-2026-0016", origen: "Monterrey", destino: "Laredo", estatus: "completado", unidad: "ECO-001", operador: "A. López" },
        { numero: "VJ-2026-0015", origen: "Altamira", destino: "Guadalajara", estatus: "programado", unidad: "ECO-007", operador: "M. Flores" },
        { numero: "VJ-2026-0014", origen: "Saltillo", destino: "Monterrey", estatus: "completado", unidad: "ECO-002", operador: "E. Ramírez" },
    ]

    const estatusBadge: { [key: string]: string } = {
        en_ruta: "bg-blue-500/15 text-blue-400 border border-blue-500/30",
        completado: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
        programado: "bg-yellow-500/15 text-yellow-400 border border-yellow-500/30",
        cancelado: "bg-red-500/15 text-red-400 border border-red-500/30",
    }

    const estatusLabel: { [key: string]: string } = {
        en_ruta: "En Ruta",
        completado: "Completado",
        programado: "Programado",
        cancelado: "Cancelado",
    }

    return (
        <div className="flex-1 space-y-6">
            {/* Header */}
            <div>
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Marzo 2026</p>
                <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Dashboard</h1>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {kpis.map((kpi, i) => (
                    <Card key={i} className={`relative overflow-hidden transition-all ${kpi.trend === "alert" ? "border-destructive/40" : "hover:shadow-md"}`}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-4 px-4">
                            <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                {kpi.title}
                            </CardTitle>
                            <kpi.icon className={`h-4 w-4 ${kpi.trend === "alert" ? "text-destructive" : "text-muted-foreground/60"}`} />
                        </CardHeader>
                        <CardContent className="pb-4 px-4">
                            <div className="text-2xl font-bold tracking-tight">{kpi.value}</div>
                            <p className={`text-xs flex items-center gap-1 mt-1.5 ${kpi.trend === "up" ? "text-emerald-500" :
                                    kpi.trend === "alert" ? "text-destructive" :
                                        "text-muted-foreground"
                                }`}>
                                {kpi.trend === "up" && <ArrowUpRight className="h-3 w-3" />}
                                {kpi.trend === "down" && <ArrowDownRight className="h-3 w-3" />}
                                {kpi.change}
                            </p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Chart + Trips Grid */}
            <div className="grid gap-4 lg:grid-cols-7">
                {/* Chart */}
                <Card className="lg:col-span-4">
                    <CardHeader className="px-5 pt-5 pb-0">
                        <CardTitle className="text-sm font-medium">Resumen Financiero</CardTitle>
                        <CardDescription className="text-xs">Ingresos vs Gastos — Últimos 6 meses</CardDescription>
                    </CardHeader>
                    <CardContent className="pt-4 pb-4 px-2">
                        <div className="h-[260px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={chartData} barGap={4}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" strokeOpacity={0.08} />
                                    <XAxis
                                        dataKey="mes"
                                        fontSize={11}
                                        tickLine={false}
                                        axisLine={false}
                                        stroke="hsl(var(--muted-foreground))"
                                    />
                                    <YAxis
                                        fontSize={11}
                                        tickLine={false}
                                        axisLine={false}
                                        stroke="hsl(var(--muted-foreground))"
                                        tickFormatter={(v: number) => `$${v / 1000}k`}
                                    />
                                    <Tooltip
                                        cursor={{ fill: "currentColor", opacity: 0.04 }}
                                        contentStyle={{
                                            backgroundColor: "hsl(var(--card))",
                                            border: "1px solid hsl(var(--border))",
                                            borderRadius: "8px",
                                            fontSize: 12,
                                        }}
                                        formatter={(v: number) =>
                                            new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)
                                        }
                                    />
                                    <Bar dataKey="ingresos" name="Ingresos" fill="hsl(var(--foreground))" radius={[3, 3, 0, 0]} opacity={0.9} />
                                    <Bar dataKey="gastos" name="Gastos" fill="hsl(var(--muted-foreground))" radius={[3, 3, 0, 0]} opacity={0.4} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* Fleet Status */}
                <Card className="lg:col-span-3 flex flex-col">
                    <CardHeader className="px-5 pt-5 pb-3">
                        <CardTitle className="text-sm font-medium">Estatus de Flota</CardTitle>
                        <CardDescription className="text-xs">8 unidades registradas</CardDescription>
                    </CardHeader>
                    <CardContent className="px-5 pb-5 flex-1">
                        <div className="space-y-3">
                            {[
                                { label: "En ruta", count: 5, color: "bg-blue-500", pct: (5 / 8) * 100 },
                                { label: "Disponibles", count: 2, color: "bg-emerald-500", pct: (2 / 8) * 100 },
                                { label: "En taller", count: 1, color: "bg-yellow-500", pct: (1 / 8) * 100 },
                            ].map((s) => (
                                <div key={s.label}>
                                    <div className="flex items-center justify-between text-xs mb-1.5">
                                        <div className="flex items-center gap-2">
                                            <span className={`h-2 w-2 rounded-full ${s.color}`} />
                                            <span className="text-muted-foreground">{s.label}</span>
                                        </div>
                                        <span className="font-medium">{s.count}</span>
                                    </div>
                                    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                                        <div className={`h-full rounded-full ${s.color}`} style={{ width: `${s.pct}%` }} />
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-5 pt-4 border-t border-border">
                            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3">Alertas</p>
                            <div className="space-y-2.5">
                                <div className="flex items-start gap-2.5 text-xs">
                                    <span className="flex shrink-0 h-4 w-4 rounded-full bg-destructive/15 items-center justify-center mt-0.5">
                                        <span className="h-1.5 w-1.5 rounded-full bg-destructive" />
                                    </span>
                                    <span className="text-muted-foreground leading-relaxed">FAC-2026-015 vencida hace 15 días — $127,500</span>
                                </div>
                                <div className="flex items-start gap-2.5 text-xs">
                                    <span className="flex shrink-0 h-4 w-4 rounded-full bg-yellow-500/15 items-center justify-center mt-0.5">
                                        <span className="h-1.5 w-1.5 rounded-full bg-yellow-500" />
                                    </span>
                                    <span className="text-muted-foreground leading-relaxed">ECO-007 requiere servicio preventivo esta semana</span>
                                </div>
                                <div className="flex items-start gap-2.5 text-xs">
                                    <span className="flex shrink-0 h-4 w-4 rounded-full bg-yellow-500/15 items-center justify-center mt-0.5">
                                        <span className="h-1.5 w-1.5 rounded-full bg-yellow-500" />
                                    </span>
                                    <span className="text-muted-foreground leading-relaxed">Stock bajo: Filtro de aceite — 2 pzas (mín. 5)</span>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Recent Trips Table */}
            <Card>
                <CardHeader className="px-5 pt-5 pb-3">
                    <CardTitle className="text-sm font-medium">Viajes Recientes</CardTitle>
                    <CardDescription className="text-xs">Últimas operaciones registradas</CardDescription>
                </CardHeader>
                <CardContent className="px-0 pb-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-border">
                                    <th className="text-left text-xs font-medium text-muted-foreground px-5 py-2.5">Viaje</th>
                                    <th className="text-left text-xs font-medium text-muted-foreground px-3 py-2.5">Ruta</th>
                                    <th className="text-left text-xs font-medium text-muted-foreground px-3 py-2.5">Unidad</th>
                                    <th className="text-left text-xs font-medium text-muted-foreground px-3 py-2.5">Operador</th>
                                    <th className="text-left text-xs font-medium text-muted-foreground px-3 py-2.5 pr-5">Estatus</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                {recentTrips.map((trip) => (
                                    <tr key={trip.numero} className="hover:bg-muted/30 transition-colors cursor-pointer">
                                        <td className="px-5 py-3 font-mono text-xs font-medium">{trip.numero}</td>
                                        <td className="px-3 py-3 text-xs text-muted-foreground">{trip.origen} → {trip.destino}</td>
                                        <td className="px-3 py-3 text-xs font-medium">{trip.unidad}</td>
                                        <td className="px-3 py-3 text-xs text-muted-foreground">{trip.operador}</td>
                                        <td className="px-3 py-3 pr-5">
                                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${estatusBadge[trip.estatus]}`}>
                                                {estatusLabel[trip.estatus]}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
