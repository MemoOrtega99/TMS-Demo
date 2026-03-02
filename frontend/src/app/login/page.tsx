"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Truck, Eye, EyeOff, Loader2 } from "lucide-react"

export default function LoginPage() {
    const router = useRouter()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    async function handleLogin(e: React.FormEvent) {
        e.preventDefault()
        setLoading(true)
        setError("")

        try {
            const formData = new URLSearchParams()
            formData.append("username", email)
            formData.append("password", password)

            const res = await fetch("http://localhost:8001/api/v1/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData.toString(),
            })

            if (res.ok) {
                const data = await res.json()
                localStorage.setItem("token", data.access_token)
                router.push("/dashboard")
            } else {
                setError("Credenciales incorrectas. Por favor verifica tu email y contraseña.")
            }
        } catch {
            // Backend no disponible — modo demo directo
            if (email === "admin@admin.com" && password === "demo2026") {
                localStorage.setItem("token", "demo-token")
                router.push("/dashboard")
            } else {
                setError("Credenciales incorrectas. Usa admin@admin.com / demo2026")
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-background flex">
            {/* Left panel - branding */}
            <div className="hidden lg:flex lg:w-1/2 bg-card border-r border-border flex-col justify-between p-12">
                <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-foreground">
                        <Truck className="size-5 text-background" />
                    </div>
                    <span className="text-lg font-semibold tracking-tight">Soluciones-TMS</span>
                </div>

                <div className="space-y-4">
                    <blockquote className="text-2xl font-medium leading-relaxed text-foreground">
                        &ldquo;El sistema que transforma la gestión de tu flota en ventaja competitiva.&rdquo;
                    </blockquote>
                    <p className="text-muted-foreground text-sm">
                        Control total de viajes, finanzas, flota e inventario — todo en un solo lugar.
                    </p>
                </div>

                <div className="space-y-3">
                    {[
                        { label: "Rentabilidad por viaje en tiempo real" },
                        { label: "Control de CxP y CxC con alertas de vencimiento" },
                        { label: "IA integrada para análisis de operaciones" },
                    ].map((feat) => (
                        <div key={feat.label} className="flex items-center gap-2.5 text-sm text-muted-foreground">
                            <div className="h-1.5 w-1.5 rounded-full bg-foreground/40" />
                            {feat.label}
                        </div>
                    ))}
                </div>
            </div>

            {/* Right panel - login form */}
            <div className="flex-1 flex flex-col items-center justify-center p-8">
                <div className="w-full max-w-sm space-y-8">
                    {/* Mobile logo */}
                    <div className="lg:hidden flex items-center gap-3 justify-center">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-foreground">
                            <Truck className="size-5 text-background" />
                        </div>
                        <span className="text-lg font-semibold">Soluciones-TMS</span>
                    </div>

                    <div className="space-y-2">
                        <h1 className="text-2xl font-semibold tracking-tight">Iniciar sesión</h1>
                        <p className="text-sm text-muted-foreground">
                            Ingresa tus credenciales para acceder al sistema
                        </p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-4">
                        <div className="space-y-1.5">
                            <label htmlFor="email" className="text-sm font-medium">
                                Correo electrónico
                            </label>
                            <input
                                id="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="admin@admin.com"
                                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors"
                            />
                        </div>

                        <div className="space-y-1.5">
                            <label htmlFor="password" className="text-sm font-medium">
                                Contraseña
                            </label>
                            <div className="relative">
                                <input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    autoComplete="current-password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                >
                                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <p className="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md px-3 py-2">
                                {error}
                            </p>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex items-center justify-center gap-2 rounded-md bg-foreground px-4 py-2.5 text-sm font-medium text-background hover:bg-foreground/90 disabled:opacity-50 transition-all"
                        >
                            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                            {loading ? "Iniciando sesión..." : "Continuar"}
                        </button>
                    </form>

                    {/* Demo credentials hint */}
                    <div className="rounded-md border border-border bg-muted/30 p-3 space-y-1.5">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Credenciales de demo</p>
                        <div className="text-xs text-muted-foreground space-y-1">
                            <p><span className="font-mono text-foreground">admin@admin.com</span></p>
                            <p><span className="font-mono text-foreground">admin123</span></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
