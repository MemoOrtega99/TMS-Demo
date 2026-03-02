"use client"

import * as React from "react"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { ArrowUpRight, ArrowDownRight, Activity, Wallet, Truck, TrendingUp, AlertTriangle } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function DashboardPage() {
    // Placeholder data - later to be fetched from API
    const kpis = [
        {
            title: "Facturación (Mes)",
            value: "$1,245,000",
            change: "+12.5%",
            trend: "up",
            icon: Wallet,
        },
        {
            title: "Viajes Activos",
            value: "14",
            change: "+2",
            trend: "up",
            icon: Truck,
        },
        {
            title: "Rentabilidad Promedio",
            value: "32.4%",
            change: "-1.2%",
            trend: "down",
            icon: Activity,
        },
        {
            title: "CxC Vencidas",
            value: "$345,000",
            change: "3 facturas",
            trend: "down",
            icon: AlertTriangle,
            alert: true
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

    return (
        <div className="flex-1 space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                    <p className="text-muted-foreground">Resumen ejecutivo y estado de flotas de Soluciones-TMS.</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {kpis.map((kpi, index) => (
                    <Card key={index} className={kpi.alert ? "border-destructive/50" : ""}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                {kpi.title}
                            </CardTitle>
                            <kpi.icon className={`h-4 w-4 ${kpi.alert ? "text-destructive" : "text-muted-foreground"}`} />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{kpi.value}</div>
                            <p className={`text-xs flex items-center gap-1 mt-1 ${kpi.trend === 'up' && !kpi.alert ? 'text-emerald-500' :
                                    kpi.alert ? 'text-destructive' : 'text-muted-foreground'
                                }`}>
                                {kpi.trend === 'up' && !kpi.alert && <ArrowUpRight className="h-3 w-3" />}
                                {kpi.trend === 'down' && !kpi.alert && <ArrowDownRight className="h-3 w-3" />}
                                {kpi.change} respecto al mes anterior
                            </p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Resumen Financiero (Últimos 6 meses)</CardTitle>
                        <CardDescription>
                            Comparativa de ingresos facturados vs gastos operativos
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="pl-2">
                        <div className="h-[300px] w-full mt-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                                    <XAxis
                                        dataKey="mes"
                                        stroke="#888888"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <YAxis
                                        stroke="#888888"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(value) => `$${value / 1000}k`}
                                    />
                                    <Tooltip
                                        cursor={{ fill: 'var(--muted)', opacity: 0.2 }}
                                        contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)' }}
                                        formatter={(value: number) => new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(value)}
                                    />
                                    <Bar dataKey="ingresos" name="Ingresos" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="gastos" name="Gastos" fill="var(--muted-foreground)" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Alertas Recientes</CardTitle>
                        <CardDescription>
                            Atención requerida en la operación
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <Alert variant="destructive" className="bg-destructive/10 border-destructive/20">
                                <AlertTriangle className="h-4 w-4" />
                                <AlertTitle>Factura Vencida (Urgente)</AlertTitle>
                                <AlertDescription>
                                    FAC-2026-015 de Grupo Bimbo venció hace 15 días. Saldo: $127,500.00
                                </AlertDescription>
                            </Alert>

                            <Alert className="border-amber-500/50 bg-amber-500/10 text-amber-500 [&>svg]:text-amber-500">
                                <AlertTriangle className="h-4 w-4" />
                                <AlertTitle>Stock bajo</AlertTitle>
                                <AlertDescription>
                                    Filtro de aceite motor — Quedan 2 pzas (Mínimo: 5)
                                </AlertDescription>
                            </Alert>

                            <Alert className="border-blue-500/50 bg-blue-500/10 text-blue-500 [&>svg]:text-blue-500">
                                <TrendingUp className="h-4 w-4" />
                                <AlertTitle>Rendimiento Anómalo</AlertTitle>
                                <AlertDescription>
                                    Unidad ECO-003 reportó 1.8 km/l en el viaje VJ-2026-0012 (Esperado: 2.2 km/l)
                                </AlertDescription>
                            </Alert>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
