"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Save, User, Phone, Mail, CreditCard, Droplets, Calendar } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"

export default function NuevoOperadorPage() {
    const router = useRouter()
    const [loading, setLoading] = useState(false)
    const [formData, setFormData] = useState({
        nombre: "",
        apellido: "",
        licencia_numero: "",
        licencia_tipo: "E",
        licencia_vigencia: "",
        telefono: "",
        salario_base: 0,
        tipo_sangre: "O+",
        estatus: "ACTIVO"
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            const res = await fetch("http://localhost:8001/api/v1/drivers", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(formData)
            })
            if (res.ok) {
                router.push("/catalogos/operadores")
            }
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6 max-w-3xl mx-auto">
            <div className="flex items-center gap-4">
                <Link href="/catalogos/operadores" className="p-2 hover:bg-muted rounded-full transition-colors">
                    <ArrowLeft className="h-5 w-5" />
                </Link>
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Operadores</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Nuevo Operador</h1>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <User className="h-4 w-4 text-muted-foreground" />
                            Información Personal
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Nombre(s)</label>
                            <input
                                required
                                type="text"
                                value={formData.nombre}
                                onChange={e => setFormData({ ...formData, nombre: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                placeholder="Ej. Juan Carlos"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Apellidos</label>
                            <input
                                required
                                type="text"
                                value={formData.apellido}
                                onChange={e => setFormData({ ...formData, apellido: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                placeholder="Ej. Pérez Martínez"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                                <Phone className="h-3 w-3" />
                                Teléfono
                            </label>
                            <input
                                type="text"
                                value={formData.telefono}
                                onChange={e => setFormData({ ...formData, telefono: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                placeholder="81 1234 5678"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                                <Droplets className="h-3 w-3" />
                                Tipo de Sangre
                            </label>
                            <select
                                value={formData.tipo_sangre}
                                onChange={e => setFormData({ ...formData, tipo_sangre: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                            >
                                {["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"].map(t => (
                                    <option key={t} value={t}>{t}</option>
                                ))}
                            </select>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <CreditCard className="h-4 w-4 text-muted-foreground" />
                            Licencia y Contrato
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Número de Licencia</label>
                            <input
                                required
                                type="text"
                                value={formData.licencia_numero}
                                onChange={e => setFormData({ ...formData, licencia_numero: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring font-mono"
                                placeholder="ABCD123456"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Tipo de Licencia</label>
                            <select
                                value={formData.licencia_tipo}
                                onChange={e => setFormData({ ...formData, licencia_tipo: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                            >
                                <option value="A">Tipo A (Federal)</option>
                                <option value="B">Tipo B (Federal carga)</option>
                                <option value="C">Tipo C (Federal 2-3 ejes)</option>
                                <option value="E">Tipo E (Federal materiales peligrosos)</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                Vigencia de Licencia
                            </label>
                            <input
                                required
                                type="date"
                                value={formData.licencia_vigencia}
                                onChange={e => setFormData({ ...formData, licencia_vigencia: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Salario Base Semanal</label>
                            <div className="relative">
                                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">$</span>
                                <input
                                    type="number"
                                    value={formData.salario_base}
                                    onChange={e => setFormData({ ...formData, salario_base: parseFloat(e.target.value) || 0 })}
                                    className="w-full pl-7 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                                    placeholder="0.00"
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <div className="flex justify-end gap-3">
                    <Link href="/catalogos/operadores" className="px-4 py-2 text-sm font-medium border border-input rounded-md hover:bg-muted transition-colors">
                        Cancelar
                    </Link>
                    <button
                        disabled={loading}
                        type="submit"
                        className="flex items-center gap-2 rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors disabled:opacity-50"
                    >
                        <Save className="h-4 w-4" />
                        {loading ? "Guardando..." : "Guardar Operador"}
                    </button>
                </div>
            </form>
        </div>
    )
}
