"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Save, Building2, Phone, Mail, Tag, MapPin } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { useToast } from "@/components/ui/ToastContext"

export default function NuevoProveedorPage() {
    const router = useRouter()
    const { toast } = useToast()
    const [loading, setLoading] = useState(false)
    const [savedFields, setSavedFields] = useState<Set<string>>(new Set())
    const [dirtyFields, setDirtyFields] = useState<Set<string>>(new Set())

    const [formData, setFormData] = useState({
        nombre: "",
        rfc: "",
        tipo: "REFACCIONES",
        direccion: "",
        telefono: "",
        email: "",
        contacto_nombre: "",
        estatus: "ACTIVO"
    })

    const markDirty = (field: string) => {
        setDirtyFields(prev => new Set(prev).add(field))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            const res = await fetch("http://localhost:8001/api/v1/suppliers", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(formData)
            })
            if (res.ok) {
                toast.success("Proveedor guardado correctamente")
                setSavedFields(new Set(dirtyFields))
                setDirtyFields(new Set())
                setTimeout(() => {
                    setSavedFields(new Set())
                    router.push("/catalogos/proveedores")
                }, 2000)
            } else {
                toast.error("Error al guardar el proveedor")
            }
        } catch (err) {
            console.error(err)
            toast.error("Error de conexión con el servidor")
        } finally {
            setLoading(false)
        }
    }

    const getFieldClass = (name: string) => {
        const base = "w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring transition-all duration-300"
        return `${base} ${savedFields.has(name) ? "field-saved" : ""}`
    }

    return (
        <div className="space-y-6 max-w-3xl mx-auto">
            <div className="flex items-center gap-4">
                <Link href="/catalogos/proveedores" className="p-2 hover:bg-muted rounded-full transition-colors">
                    <ArrowLeft className="h-5 w-5" />
                </Link>
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Proveedores</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Nuevo Proveedor</h1>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <Building2 className="h-4 w-4 text-muted-foreground" />
                            Información Fiscal y Tipo
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-4">
                        <div className="col-span-2 space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Nombre / Razón Social</label>
                            <input
                                required
                                type="text"
                                value={formData.nombre}
                                onChange={e => {
                                    setFormData({ ...formData, nombre: e.target.value })
                                    markDirty("nombre")
                                }}
                                className={getFieldClass("nombre")}
                                placeholder="Ej. Llantera del Norte S.A."
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">RFC</label>
                            <input
                                required
                                type="text"
                                value={formData.rfc}
                                onChange={e => {
                                    setFormData({ ...formData, rfc: e.target.value })
                                    markDirty("rfc")
                                }}
                                className={`${getFieldClass("rfc")} font-mono`}
                                placeholder="ABCD123456EFG"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                                <Tag className="h-3 w-3" />
                                Tipo de Proveedor
                            </label>
                            <select
                                value={formData.tipo}
                                onChange={e => {
                                    setFormData({ ...formData, tipo: e.target.value })
                                    markDirty("tipo")
                                }}
                                className={getFieldClass("tipo")}
                            >
                                <option value="COMBUSTIBLE">Combustible</option>
                                <option value="REFACCIONES">Refacciones</option>
                                <option value="SERVICIOS">Servicios / Taller</option>
                                <option value="CASETAS">Casetas</option>
                                <option value="OTRO">Otro</option>
                            </select>
                        </div>
                        <div className="col-span-2 space-y-2">
                            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                Dirección
                            </label>
                            <input
                                type="text"
                                value={formData.direccion}
                                onChange={e => {
                                    setFormData({ ...formData, direccion: e.target.value })
                                    markDirty("direccion")
                                }}
                                className={getFieldClass("direccion")}
                                placeholder="Dirección completa"
                            />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <Mail className="h-4 w-4 text-muted-foreground" />
                            Contacto
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-4">
                        <div className="col-span-2 space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Nombre de Contacto</label>
                            <input
                                type="text"
                                value={formData.contacto_nombre}
                                onChange={e => {
                                    setFormData({ ...formData, contacto_nombre: e.target.value })
                                    markDirty("contacto_nombre")
                                }}
                                className={getFieldClass("contacto_nombre")}
                                placeholder="Ej. Marcos Rodríguez"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Teléfono</label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                                <input
                                    type="text"
                                    value={formData.telefono}
                                    onChange={e => {
                                        setFormData({ ...formData, telefono: e.target.value })
                                        markDirty("telefono")
                                    }}
                                    className={`${getFieldClass("telefono")} pl-9`}
                                    placeholder="81 1234 5678"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground">Correo Electrónico</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                                <input
                                    type="email"
                                    value={formData.email}
                                    onChange={e => {
                                        setFormData({ ...formData, email: e.target.value })
                                        markDirty("email")
                                    }}
                                    className={`${getFieldClass("email")} pl-9`}
                                    placeholder="correo@proveedor.com"
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <div className="flex justify-end gap-3">
                    <Link href="/catalogos/proveedores" className="px-4 py-2 text-sm font-medium border border-input rounded-md hover:bg-muted transition-colors">
                        Cancelar
                    </Link>
                    <button
                        disabled={loading}
                        type="submit"
                        className="flex items-center gap-2 rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors disabled:opacity-50"
                    >
                        <Save className="h-4 w-4" />
                        {loading ? "Guardando..." : "Guardar Proveedor"}
                    </button>
                </div>
            </form>
        </div>
    )
}

