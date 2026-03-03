"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SheetContent, SheetHeader, SheetTitle, SheetFooter } from "@/components/ui/sheet"
import { useToast } from "@/components/ui/ToastContext"

interface InventoryItemFormProps {
    onSuccess: () => void
}

export function InventoryItemForm({ onSuccess }: InventoryItemFormProps) {
    const { toast } = useToast()
    const [loading, setLoading] = useState(false)
    const [savedFields, setSavedFields] = useState<Set<string>>(new Set())

    const { register, handleSubmit, reset, formState: { dirtyFields } } = useForm({
        defaultValues: {
            codigo: "",
            nombre: "",
            categoria: "",
            stock_actual: 0,
            stock_minimo: 0,
            unidad_medida: "pza",
            precio_promedio: 0,
            ubicacion: ""
        }
    })

    const onSubmit = async (data: any) => {
        setLoading(true)
        try {
            const response = await fetch("http://localhost:8001/api/v1/inventory", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({
                    ...data,
                    categoria: data.categoria.toLowerCase(),
                    stock_actual: Number(data.stock_actual),
                    stock_minimo: Number(data.stock_minimo),
                    costo_promedio: Number(data.precio_promedio)
                })
            })

            if (response.ok) {
                toast.success("Artículo registrado correctamente")
                const currentDirty = new Set(Object.keys(dirtyFields))
                setSavedFields(currentDirty)

                setTimeout(() => {
                    setSavedFields(new Set())
                    reset()
                    onSuccess()
                }, 2000)
            } else {
                toast.error("Error al registrar el artículo")
            }
        } catch (error) {
            console.error("Error creating inventory item:", error)
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
                <SheetTitle>Nuevo Artículo de Inventario</SheetTitle>
            </SheetHeader>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-4 px-1">
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Código</label>
                        <Input
                            {...register("codigo", { required: true })}
                            placeholder="Ej: REF-005"
                            className={getHighlightClass("codigo")}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Categoría</label>
                        <select
                            {...register("categoria", { required: true })}
                            className={`w-full flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring ${getHighlightClass("categoria")}`}
                        >
                            <option value="">Seleccionar...</option>
                            <option value="refacciones">Refacciones</option>
                            <option value="llantas">Llantas</option>
                            <option value="lubricantes">Lubricantes</option>
                            <option value="herramientas">Herramientas</option>
                            <option value="combustible">Combustible</option>
                        </select>
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Nombre del Artículo</label>
                    <Input
                        {...register("nombre", { required: true })}
                        placeholder="Descripción completa del artículo"
                        className={getHighlightClass("nombre")}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Stock Actual</label>
                        <Input
                            type="number"
                            {...register("stock_actual", { required: true })}
                            className={getHighlightClass("stock_actual")}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Stock Mínimo</label>
                        <Input
                            type="number"
                            {...register("stock_minimo", { required: true })}
                            className={getHighlightClass("stock_minimo")}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Unidad Medida</label>
                        <Input
                            {...register("unidad_medida", { required: true })}
                            placeholder="Ej: pza, l, jgo"
                            className={getHighlightClass("unidad_medida")}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Precio Promedio ($)</label>
                        <Input
                            type="number"
                            step="0.01"
                            {...register("precio_promedio", { required: true })}
                            className={getHighlightClass("precio_promedio")}
                        />
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Ubicación</label>
                    <Input
                        {...register("ubicacion")}
                        placeholder="Ej: Estante A1, Bodega Principal"
                        className={getHighlightClass("ubicacion")}
                    />
                </div>

                <SheetFooter className="pt-4">
                    <Button type="submit" disabled={loading} className="w-full">
                        {loading ? "Registrando..." : "Registrar Artículo"}
                    </Button>
                </SheetFooter>
            </form>
        </SheetContent>
    )
}
