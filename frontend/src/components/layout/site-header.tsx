"use client"

import * as React from "react"
import { Bell, Search, Menu, LogOut } from "lucide-react"
import { PanelLeft } from "lucide-react"
import { useSidebarState } from "@/components/layout/app-sidebar"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { ThemeToggle } from "@/components/theme-toggle"

export function SiteHeader() {
    const { expanded, setExpanded, mobile, setMobileOpen } = useSidebarState()
    const router = useRouter()

    const handleLogout = () => {
        localStorage.removeItem("token")
        router.push("/login")
    }

    return (
        <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center justify-between gap-2 border-b border-border bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex items-center gap-2">
                {/* Desktop toggle */}
                <Button
                    variant="ghost"
                    size="icon"
                    className="hidden md:flex h-7 w-7"
                    onClick={() => setExpanded(!expanded)}
                    title="Toggle sidebar (Ctrl+B)"
                >
                    <PanelLeft className="h-4 w-4" />
                    <span className="sr-only">Toggle Sidebar</span>
                </Button>

                {/* Mobile hamburger */}
                <Button
                    variant="ghost"
                    size="icon"
                    className="md:hidden"
                    onClick={() => setMobileOpen(true)}
                >
                    <Menu className="size-5" />
                    <span className="sr-only">Abrir menú</span>
                </Button>
            </div>

            <div className="flex flex-1 items-center justify-end gap-4 md:gap-6">
                <div className="w-full max-w-sm hidden md:flex">
                    <div className="relative w-full">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            type="search"
                            placeholder="Buscar viajes, placas, facturas..."
                            className="w-full bg-background pl-9 md:w-[300px] lg:w-[400px] rounded-full border-muted-foreground/20 focus-visible:ring-primary/20 hover:border-muted-foreground/40 transition-colors"
                        />
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <ThemeToggle />
                    <Button variant="ghost" size="icon" className="relative group text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-full transition-colors">
                        <Bell className="h-5 w-5" />
                        <span className="absolute right-1.5 top-1.5 flex h-2 w-2 rounded-full bg-destructive animate-pulse" />
                        <span className="sr-only">Notificaciones</span>
                    </Button>
                    <div className="h-5 w-px bg-border mx-1" />
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={handleLogout}
                        className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-full transition-colors"
                        title="Cerrar sesión"
                    >
                        <LogOut className="h-5 w-5" />
                        <span className="sr-only">Cerrar sesión</span>
                    </Button>
                </div>
            </div>
        </header>
    )
}
