"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, Save } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export default function NuevoViajePage() {
    const router = useRouter()
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    // We keep this simple for the demo. Normally we would fetch catalogs for these dropdowns.
    const [formData, setFormData] = useState({
        numero_viaje: `VJ-${new Date().getFullYear()}-${Math.floor(Math.random() * 10000).toString().padStart(4, "0")}`,
        origen: "",
        destino: "",
        fecha_programada: new Date().toISOString().split("T")[0],
        tarifa_cliente: "",
        estatus: "programado"
    })

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError("")

        try {
            const token = localStorage.getItem("token")
            const response = await fetch("http://localhost:8001/api/v1/trips", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { "Authorization": `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    ...formData,
                    tarifa_cliente: formData.tarifa_cliente ? parseFloat(formData.tarifa_cliente) : 0
                })
            })

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.detail || "Error al crear el viaje")
            }

            router.push("/operaciones/viajes")
            router.refresh()
        } catch (err: any) {
            setError(err.message)
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6 max-w-2xl mx-auto">
            <div className="flex items-center gap-4">
                <Link href="/operaciones/viajes" className="p-2 -ml-2 hover:bg-muted rounded-full transition-colors text-muted-foreground hover:text-foreground">
                    <ArrowLeft className="h-5 w-5" />
                </Link>
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Operaciones</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Nuevo Viaje</h1>
                </div>
            </div>

            <Card>
                <CardContent className="pt-6">
                    {error && (
                        <div className="mb-6 p-3 bg-destructive/15 text-destructive border border-destructive/30 rounded-md text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Número de Viaje</label>
                            <input
                                required
                                name="numero_viaje"
                                value={formData.numero_viaje}
                                onChange={handleChange}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring font-mono"
                            />
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Origen</label>
                                <input
                                    name="origen"
                                    value={formData.origen}
                                    onChange={handleChange}
                                    placeholder="Ej. Monterrey, NL"
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Destino</label>
                                <input
                                    name="destino"
                                    value={formData.destino}
                                    onChange={handleChange}
                                    placeholder="Ej. Laredo, TX"
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Fecha Programada</label>
                                <input
                                    type="date"
                                    name="fecha_programada"
                                    value={formData.fecha_programada}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Tarifa Cliente (MXN)</label>
                                <input
                                    type="number"
                                    name="tarifa_cliente"
                                    value={formData.tarifa_cliente}
                                    onChange={handleChange}
                                    placeholder="0.00"
                                    step="0.01"
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Estatus Inicial</label>
                            <select
                                name="estatus"
                                value={formData.estatus}
                                onChange={handleChange}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring capitalize"
                            >
                                <option value="programado">Programado</option>
                                <option value="asignado">Asignado</option>
                            </select>
                        </div>

                        <div className="pt-4 flex justify-end gap-3">
                            <Link href="/operaciones/viajes" className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-md transition-colors">
                                Cancelar
                            </Link>
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-background bg-foreground hover:bg-foreground/90 rounded-md transition-colors disabled:opacity-50"
                            >
                                <Save className="h-4 w-4" />
                                {loading ? "Guardando..." : "Guardar Viaje"}
                            </button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}
