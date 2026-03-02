"use client"

import React, { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { AppSidebar, useSidebarState } from "@/components/layout/app-sidebar"
import { SiteHeader } from "@/components/layout/site-header"
import { Loader2 } from "lucide-react"

const SIDEBAR_EXPANDED = 240
const SIDEBAR_COLLAPSED = 48

function MainContent({ children }: { children: React.ReactNode }) {
    const { expanded, mobile } = useSidebarState()
    const ml = mobile ? 0 : (expanded ? SIDEBAR_EXPANDED : SIDEBAR_COLLAPSED)

    return (
        <div
            style={{ marginLeft: ml }}
            className="flex flex-col min-h-screen transition-[margin-left] duration-200 ease-linear"
        >
            <SiteHeader />
            <main className="flex-1 overflow-y-auto p-4 md:p-6">
                {children}
            </main>
        </div>
    )
}

export default function MainLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const router = useRouter()
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

    useEffect(() => {
        const token = localStorage.getItem("token")
        if (!token) {
            router.replace("/login")
        } else {
            setIsAuthenticated(true)
        }
    }, [router])

    if (isAuthenticated === null) {
        return (
            <div className="min-h-screen flex text-muted-foreground items-center justify-center bg-background">
                <Loader2 className="h-8 w-8 animate-spin" />
            </div>
        )
    }

    return (
        <>
            <AppSidebar />
            <MainContent>{children}</MainContent>
        </>
    )
}
