"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SheetContent, SheetHeader, SheetTitle, SheetFooter } from "@/components/ui/sheet"
import { useToast } from "@/components/ui/ToastContext"

interface PurchaseOrderFormProps {
    onSuccess: () => void
}

export function PurchaseOrderForm({ onSuccess }: PurchaseOrderFormProps) {
    console.log("DEBUG: PurchaseOrderForm rendering");
    const { toast } = useToast()
    const [suppliers, setSuppliers] = useState<{ id: number; nombre: string }[]>([])
    const [loading, setLoading] = useState(false)
    const [savedFields, setSavedFields] = useState<Set<string>>(new Set())

    const { register, handleSubmit, reset, formState: { dirtyFields } } = useForm({
        defaultValues: {
            numero_orden: "",
            proveedor_id: "",
            fecha_orden: new Date().toISOString().split("T")[0],
            fecha_entrega: "",
            total: 0,
            items: 0,
            estatus: "PENDIENTE"
        }
    })

    useEffect(() => {
        fetch("http://localhost:8001/api/v1/suppliers", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        })
            .then(r => r.json())
            .then(data => {
                if (Array.isArray(data?.items)) setSuppliers(data.items)
            })
            .catch(err => console.error("Error fetching suppliers:", err))
    }, [])

    const onSubmit = async (data: any) => {
        setLoading(true)
        try {
            const response = await fetch("http://localhost:8001/api/v1/purchase-orders", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({
                    ...data,
                    total: Number(data.total),
                    items: Number(data.items),
                    proveedor_id: Number(data.proveedor_id),
                    estatus: data.estatus.toLowerCase(),
                    fecha_entrega: data.fecha_entrega || null
                })
            })

            if (response.ok) {
                toast.success("Orden de compra creada correctamente")
                const currentDirty = new Set(Object.keys(dirtyFields))
                setSavedFields(currentDirty)

                setTimeout(() => {
                    setSavedFields(new Set())
                    reset()
                    onSuccess()
                }, 2000)
            } else {
                toast.error("Error al crear la orden de compra")
            }
        } catch (error) {
            console.error("Error creating purchase order:", error)
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
                <SheetTitle>Nueva Orden de Compra</SheetTitle>
            </SheetHeader>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-4 px-1">
                <div className="space-y-2">
                    <label className="text-sm font-medium">Número de Orden</label>
                    <Input
                        {...register("numero_orden", { required: true })}
                        placeholder="Ej: PO-2026-005"
                        className={getHighlightClass("numero_orden")}
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Proveedor</label>
                    <select
                        {...register("proveedor_id", { required: true })}
                        className={`w-full flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring ${getHighlightClass("proveedor_id")}`}
                    >
                        <option value="">Seleccionar proveedor...</option>
                        {suppliers.map(s => (
                            <option key={s.id} value={s.id}>{s.nombre}</option>
                        ))}
                    </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Fecha Orden</label>
                        <Input
                            type="date"
                            {...register("fecha_orden", { required: true })}
                            className={getHighlightClass("fecha_orden")}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Fecha Entrega</label>
                        <Input
                            type="date"
                            {...register("fecha_entrega")}
                            className={getHighlightClass("fecha_entrega")}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Total ($)</label>
                        <Input
                            type="number"
                            step="0.01"
                            {...register("total", { required: true })}
                            className={getHighlightClass("total")}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Cant. Artículos</label>
                        <Input
                            type="number"
                            {...register("items", { required: true })}
                            className={getHighlightClass("items")}
                        />
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Estatus Inicial</label>
                    <select
                        {...register("estatus")}
                        className={`w-full flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring ${getHighlightClass("estatus")}`}
                    >
                        <option value="pendiente">Pendiente</option>
                        <option value="recibida">Recibida</option>
                    </select>
                </div>

                <SheetFooter className="pt-4">
                    <Button type="submit" disabled={loading} className="w-full">
                        {loading ? "Guardando..." : "Crear Orden"}
                    </Button>
                </SheetFooter>
            </form>
        </SheetContent>
    )
}
