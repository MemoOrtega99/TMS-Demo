"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SheetContent, SheetHeader, SheetTitle, SheetFooter } from "@/components/ui/sheet"
import { useToast } from "@/components/ui/ToastContext"

interface InvoiceFormProps {
    tipo: "POR_COBRAR" | "POR_PAGAR"
    onSuccess: () => void
}

export function InvoiceForm({ tipo, onSuccess }: InvoiceFormProps) {
    const { toast } = useToast()
    const [entidades, setEntidades] = useState<{ id: number; nombre: string }[]>([])
    const [loading, setLoading] = useState(false)
    const [savedFields, setSavedFields] = useState<Set<string>>(new Set())

    const { register, handleSubmit, reset, watch, setValue, formState: { dirtyFields } } = useForm({
        defaultValues: {
            numero_factura: "",
            tipo: tipo,
            fecha_factura: new Date().toISOString().split("T")[0],
            fecha_vencimiento: "",
            subtotal: 0,
            iva: 0,
            total: 0,
            concepto: "",
            cliente_id: undefined as number | undefined,
            proveedor_id: undefined as number | undefined,
        }
    })

    const subtotal = watch("subtotal")
    const iva = watch("iva")

    useEffect(() => {
        const totalCalculado = Number(subtotal) + Number(iva)
        setValue("total", totalCalculado)
    }, [subtotal, iva, setValue])

    useEffect(() => {
        const endpoint = tipo === "POR_COBRAR" ? "clients" : "suppliers"
        fetch(`http://localhost:8001/api/v1/${endpoint}`, {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        })
            .then(r => r.json())
            .then(data => {
                if (Array.isArray(data?.items)) setEntidades(data.items)
            })
    }, [tipo])

    const onSubmit = async (data: any) => {
        setLoading(true)
        try {
            const response = await fetch("http://localhost:8001/api/v1/invoices", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({
                    ...data,
                    subtotal: Number(data.subtotal),
                    iva: Number(data.iva),
                    total: Number(data.total),
                    cliente_id: tipo === "POR_COBRAR" ? Number(data.cliente_id) : null,
                    proveedor_id: tipo === "POR_PAGAR" ? Number(data.proveedor_id) : null,
                })
            })
            if (response.ok) {
                toast.success("Factura creada correctamente")
                const currentDirty = new Set(Object.keys(dirtyFields))
                setSavedFields(currentDirty)

                setTimeout(() => {
                    setSavedFields(new Set())
                    reset()
                    onSuccess()
                }, 2000)
            } else {
                toast.error("Error al crear la factura")
            }
        } catch (error) {
            console.error("Error creating invoice:", error)
            toast.error("Error de conexión")
        } finally {
            setLoading(false)
        }
    }

    const getHighlightClass = (name: string) => {
        return savedFields.has(name) ? "field-saved" : ""
    }

    return (
        <SheetContent className="sm:max-w-md overflow-y-auto">
            <SheetHeader>
                <SheetTitle>Nueva factura {tipo === "POR_COBRAR" ? "por cobrar" : "por pagar"}</SheetTitle>
            </SheetHeader>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-4 px-1">
                <div className="space-y-2">
                    <label className="text-sm font-medium">Número de Factura</label>
                    <Input
                        {...register("numero_factura", { required: true })}
                        placeholder="Ej: FAC-001"
                        className={getHighlightClass("numero_factura")}
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium">{tipo === "POR_COBRAR" ? "Cliente" : "Proveedor"}</label>
                    <select
                        {...register(tipo === "POR_COBRAR" ? "cliente_id" : "proveedor_id", { required: true })}
                        className={`w-full flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring ${getHighlightClass(tipo === "POR_COBRAR" ? "cliente_id" : "proveedor_id")}`}
                    >
                        <option value="">Seleccionar...</option>
                        {entidades.map(e => (
                            <option key={e.id} value={e.id}>{e.nombre}</option>
                        ))}
                    </select>
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium">Fecha de Factura</label>
                    <Input
                        type="date"
                        {...register("fecha_factura", { required: true })}
                        className={getHighlightClass("fecha_factura")}
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium">Fecha de Vencimiento</label>
                    <Input
                        type="date"
                        {...register("fecha_vencimiento")}
                        className={getHighlightClass("fecha_vencimiento")}
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Subtotal</label>
                        <Input
                            type="number"
                            step="0.01"
                            {...register("subtotal", { required: true })}
                            className={getHighlightClass("subtotal")}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">IVA</label>
                        <Input
                            type="number"
                            step="0.01"
                            {...register("iva")}
                            className={getHighlightClass("iva")}
                        />
                    </div>
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium">Total</label>
                    <Input type="number" step="0.01" {...register("total")} disabled className="bg-muted" />
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium">Concepto</label>
                    <Input
                        {...register("concepto", { required: true })}
                        placeholder="Descripción del servicio..."
                        className={getHighlightClass("concepto")}
                    />
                </div>
                <SheetFooter className="pt-4">
                    <Button type="submit" disabled={loading} className="w-full">
                        {loading ? "Guardando..." : "Crear Factura"}
                    </Button>
                </SheetFooter>
            </form>
        </SheetContent>
    )
}

