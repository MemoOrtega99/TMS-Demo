"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, Save } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export default function NuevoDollyPage() {
    const router = useRouter()
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    const [formData, setFormData] = useState({
        numero_economico: "",
        marca: "",
        modelo: "",
        anio: new Date().getFullYear(),
        placas: "",
        estatus: "DISPONIBLE"
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
            const response = await fetch("http://localhost:8001/api/v1/dollies", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { "Authorization": `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    ...formData,
                    anio: parseInt(formData.anio as any) || new Date().getFullYear(),
                })
            })

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.detail || "Error al registrar el dolly")
            }

            router.push("/flota/dolly")
            router.refresh()
        } catch (err: any) {
            setError(err.message)
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6 max-w-3xl mx-auto">
            <div className="flex items-center gap-4">
                <Link href="/flota/dolly" className="p-2 -ml-2 hover:bg-muted rounded-full transition-colors text-muted-foreground hover:text-foreground">
                    <ArrowLeft className="h-5 w-5" />
                </Link>
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Flota</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Nuevo Dolly</h1>
                </div>
            </div>

            <Card>
                <CardContent className="pt-6">
                    {error && (
                        <div className="mb-6 p-3 bg-destructive/15 text-destructive border border-destructive/30 rounded-md text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Número Económico *</label>
                                <input
                                    required
                                    name="numero_economico"
                                    value={formData.numero_economico}
                                    onChange={handleChange}
                                    placeholder="Ej. DOL-001"
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring font-mono"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Placas</label>
                                <input
                                    name="placas"
                                    value={formData.placas}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring font-mono uppercase"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                            <div className="space-y-2 flex-1">
                                <label className="text-sm font-medium">Marca</label>
                                <input
                                    name="marca"
                                    value={formData.marca}
                                    onChange={handleChange}
                                    placeholder="Ej. MATRA"
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                />
                            </div>
                            <div className="space-y-2 flex-1">
                                <label className="text-sm font-medium">Modelo</label>
                                <input
                                    name="modelo"
                                    value={formData.modelo}
                                    onChange={handleChange}
                                    placeholder=""
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                />
                            </div>
                            <div className="space-y-2 w-full sm:w-32">
                                <label className="text-sm font-medium">Año</label>
                                <input
                                    type="number"
                                    name="anio"
                                    value={formData.anio}
                                    onChange={handleChange}
                                    min="1980"
                                    max="2035"
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Estatus Inicial</label>
                                <select
                                    name="estatus"
                                    value={formData.estatus}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                >
                                    <option value="DISPONIBLE">Disponible</option>
                                    <option value="TALLER">En Taller</option>
                                    <option value="BAJA">Baja</option>
                                </select>
                            </div>
                        </div>

                        <div className="pt-4 flex justify-end gap-3 border-t border-border mt-6">
                            <Link href="/flota/dolly" className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-md transition-colors">
                                Cancelar
                            </Link>
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-background bg-foreground hover:bg-foreground/90 rounded-md transition-colors disabled:opacity-50"
                            >
                                <Save className="h-4 w-4" />
                                {loading ? "Registrando..." : "Registrar Dolly"}
                            </button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}
