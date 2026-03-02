"use client"

import * as React from "react"
import { useEffect } from "react"
import { usePathname } from "next/navigation"
import Link from "next/link"
import {
    LayoutDashboard, Truck, Wallet, Users, Package,
    Bell, Bot, LogOut, ChevronDown, Fuel, ShoppingCart,
    PanelLeft, X
} from "lucide-react"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

const SIDEBAR_EXPANDED_WIDTH = 240  // px
const SIDEBAR_COLLAPSED_WIDTH = 48  // px (icon-only)

// Context for sidebar state
const SidebarCtx = React.createContext<{
    expanded: boolean
    setExpanded: (v: boolean) => void
    mobile: boolean
    mobileOpen: boolean
    setMobileOpen: (v: boolean) => void
}>({
    expanded: true,
    setExpanded: () => { },
    mobile: false,
    mobileOpen: false,
    setMobileOpen: () => { },
})

export function useSidebarState() {
    return React.useContext(SidebarCtx)
}

const navGroups = [
    { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard, single: true },
    {
        title: "Operaciones", icon: Truck, single: false,
        items: [{ title: "Viajes", url: "/operaciones/viajes" }],
    },
    {
        title: "Flota", icon: Truck, single: false,
        items: [
            { title: "Unidades", url: "/flota/unidades" },
            { title: "Remolques", url: "/flota/remolques" },
            { title: "Dollies", url: "/flota/dolly" },
        ],
    },
    { title: "Finanzas", icon: Wallet, single: true, url: "/finanzas" },
    {
        title: "Catálogos", icon: Users, single: false,
        items: [
            { title: "Clientes", url: "/catalogos/clientes" },
            { title: "Proveedores", url: "/catalogos/proveedores" },
            { title: "Operadores", url: "/catalogos/operadores" },
        ],
    },
    {
        title: "Diesel", icon: Fuel, single: false,
        items: [
            { title: "Cargas", url: "/diesel/cargas" },
            { title: "Rendimientos", url: "/diesel/rendimientos" },
        ],
    },
    { title: "Compras", url: "/compras", icon: ShoppingCart, single: true },
    { title: "Inventario", url: "/inventario", icon: Package, single: true },
]

function NavItem({ group, expanded, pathname }: {
    group: (typeof navGroups)[0]
    expanded: boolean
    pathname: string
}) {
    const isActive = (url: string) => pathname === url || pathname.startsWith(url + "/")

    if (group.single) {
        const active = isActive(group.url!)
        return (
            <Link
                href={group.url!}
                title={!expanded ? group.title : undefined}
                className={cn(
                    "flex items-center gap-3 rounded-md px-2 py-2 text-sm transition-colors",
                    "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                    active ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium" : "text-sidebar-foreground/70",
                    !expanded && "justify-center px-0"
                )}
            >
                <group.icon className="h-4 w-4 shrink-0" />
                {expanded && <span className="truncate">{group.title}</span>}
            </Link>
        )
    }

    const groupActive = group.items?.some(it => isActive(it.url))
    return (
        <Collapsible defaultOpen={groupActive} disabled={!expanded}>
            <CollapsibleTrigger asChild>
                <button
                    title={!expanded ? group.title : undefined}
                    className={cn(
                        "flex w-full items-center gap-3 rounded-md px-2 py-2 text-sm transition-colors",
                        "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                        groupActive ? "text-sidebar-foreground font-medium" : "text-sidebar-foreground/70",
                        !expanded && "justify-center px-0"
                    )}
                >
                    <group.icon className="h-4 w-4 shrink-0" />
                    {expanded && (
                        <>
                            <span className="truncate flex-1 text-left">{group.title}</span>
                            <ChevronDown className="h-3.5 w-3.5 shrink-0 transition-transform duration-200 group-data-[state=open]:rotate-180" />
                        </>
                    )}
                </button>
            </CollapsibleTrigger>
            {expanded && (
                <CollapsibleContent>
                    <div className="ml-7 mt-0.5 flex flex-col gap-0.5 border-l border-sidebar-border pl-2">
                        {group.items?.map(item => (
                            <Link
                                key={item.url}
                                href={item.url}
                                className={cn(
                                    "block rounded-md px-2 py-1.5 text-sm transition-colors",
                                    isActive(item.url)
                                        ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                                        : "text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent"
                                )}
                            >
                                {item.title}
                            </Link>
                        ))}
                    </div>
                </CollapsibleContent>
            )}
        </Collapsible>
    )
}

function SidebarContent({ expanded }: { expanded: boolean }) {
    const pathname = usePathname()

    return (
        <div className="flex flex-col h-full bg-sidebar text-sidebar-foreground">
            {/* Logo */}
            <div className="flex h-16 shrink-0 items-center border-b border-sidebar-border px-3">
                <Link href="/dashboard" className="flex items-center gap-2.5 font-semibold min-w-0">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sidebar-foreground text-sidebar">
                        <Truck className="size-4" />
                    </div>
                    {expanded && <span className="truncate text-sm text-sidebar-foreground">Soluciones-TMS</span>}
                </Link>
            </div>

            {/* Nav */}
            <nav className="flex-1 overflow-y-auto py-3 px-2">
                <div className="flex flex-col gap-0.5">
                    {navGroups.map(group => (
                        <NavItem key={group.title} group={group} expanded={expanded} pathname={pathname} />
                    ))}
                </div>
            </nav>

            {/* Footer */}
            <div className="shrink-0 border-t border-sidebar-border p-2 space-y-0.5">
                <Link
                    href="/ia"
                    title={!expanded ? "Asistente IA" : undefined}
                    className={cn(
                        "flex items-center gap-3 rounded-md px-2 py-2 text-sm transition-colors",
                        "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                        !expanded && "justify-center px-0"
                    )}
                >
                    <Bot className="h-4 w-4 shrink-0" />
                    {expanded && <span>Asistente IA</span>}
                </Link>
                <Link
                    href="/notificaciones"
                    title={!expanded ? "Notificaciones" : undefined}
                    className={cn(
                        "flex items-center gap-3 rounded-md px-2 py-2 text-sm transition-colors",
                        "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                        !expanded && "justify-center px-0"
                    )}
                >
                    <Bell className="h-4 w-4 shrink-0" />
                    {expanded && <span>Notificaciones</span>}
                </Link>
                <div className={cn(
                    "flex items-center gap-3 rounded-md px-2 py-2 mt-1",
                    !expanded && "justify-center px-0"
                )}>
                    <Avatar className="h-8 w-8 rounded-lg shrink-0">
                        <AvatarFallback className="rounded-lg bg-sidebar-accent text-sidebar-accent-foreground text-xs">CM</AvatarFallback>
                    </Avatar>
                    {expanded && (
                        <div className="flex-1 min-w-0">
                            <p className="truncate text-sm font-semibold text-sidebar-foreground">Carlos Mendoza</p>
                            <p className="truncate text-xs text-sidebar-foreground/60">Administrador</p>
                        </div>
                    )}
                    {expanded && <LogOut className="h-4 w-4 text-sidebar-foreground/40 shrink-0" />}
                </div>
            </div>
        </div>
    )
}

export function AppSidebar() {
    const [expanded, setExpanded] = React.useState(true)
    const [mobile, setMobile] = React.useState(false)
    const [mobileOpen, setMobileOpen] = React.useState(false)

    React.useEffect(() => {
        const mql = window.matchMedia("(max-width: 768px)")
        const onChange = () => {
            setMobile(mql.matches)
            if (mql.matches) setExpanded(false)
        }
        onChange()
        mql.addEventListener("change", onChange)
        return () => mql.removeEventListener("change", onChange)
    }, [])

    useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "b") {
                e.preventDefault()
                if (mobile) setMobileOpen(o => !o)
                else setExpanded(o => !o)
            }
        }
        window.addEventListener("keydown", handleKey)
        return () => window.removeEventListener("keydown", handleKey)
    }, [mobile])

    const sidebarWidth = mobile ? 0 : (expanded ? SIDEBAR_EXPANDED_WIDTH : SIDEBAR_COLLAPSED_WIDTH)

    return (
        <SidebarCtx.Provider value={{ expanded, setExpanded, mobile, mobileOpen, setMobileOpen }}>
            {/* Desktop sidebar — fixed position, pushes content via margin */}
            {!mobile && (
                <aside
                    style={{ width: sidebarWidth }}
                    className="fixed inset-y-0 left-0 z-30 flex flex-col overflow-hidden transition-[width] duration-200 ease-linear border-r border-sidebar-border"
                >
                    <SidebarContent expanded={expanded} />
                </aside>
            )}

            {/* Mobile overlay sidebar */}
            {mobile && mobileOpen && (
                <>
                    <div
                        className="fixed inset-0 z-40 bg-black/50"
                        onClick={() => setMobileOpen(false)}
                    />
                    <aside className="fixed inset-y-0 left-0 z-50 w-60 flex flex-col border-r border-sidebar-border">
                        <button
                            onClick={() => setMobileOpen(false)}
                            className="absolute right-2 top-4 p-1.5 rounded-md text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent z-10"
                        >
                            <X className="h-4 w-4" />
                        </button>
                        <SidebarContent expanded={true} />
                    </aside>
                </>
            )}
        </SidebarCtx.Provider>
    )
}

