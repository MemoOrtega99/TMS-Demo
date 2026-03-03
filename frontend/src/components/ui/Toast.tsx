'use client'

import { useEffect, useState } from 'react'
import { CheckCircle2, XCircle, AlertTriangle, Info, X } from 'lucide-react'

export interface ToastData {
    id: number
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    title?: string
}

interface ToastProps {
    data: ToastData
    onClose: (id: number) => void
    duration?: number
}

const CONFIG = {
    success: {
        icon: CheckCircle2,
        color: '#10b981', // emerald-500
        bg: 'rgba(16, 185, 129, 0.1)',
        title: 'Completado',
    },
    error: {
        icon: XCircle,
        color: '#ef4444', // red-500
        bg: 'rgba(239, 68, 68, 0.1)',
        title: 'Error',
    },
    warning: {
        icon: AlertTriangle,
        color: '#f59e0b', // amber-500
        bg: 'rgba(245, 158, 11, 0.1)',
        title: 'Atención',
    },
    info: {
        icon: Info,
        color: '#3b82f6', // blue-500
        bg: 'rgba(59, 130, 246, 0.1)',
        title: 'Info',
    },
}

export default function Toast({ data, onClose, duration = 4000 }: ToastProps) {
    const [visible, setVisible] = useState(false)
    const [progress, setProgress] = useState(100)
    const cfg = CONFIG[data.type]
    const Icon = cfg.icon

    useEffect(() => {
        // Trigger slide-in
        requestAnimationFrame(() => setVisible(true))

        const startTime = Date.now()
        const interval = setInterval(() => {
            const elapsed = Date.now() - startTime
            const remaining = Math.max(0, 100 - (elapsed / duration) * 100)
            setProgress(remaining)
            if (remaining === 0) {
                clearInterval(interval)
                handleClose()
            }
        }, 50)

        return () => clearInterval(interval)
    }, [duration])

    const handleClose = () => {
        setVisible(false)
        setTimeout(() => onClose(data.id), 300)
    }

    return (
        <div
            className="pointer-events-auto"
            style={{
                transform: visible ? 'translateX(0)' : 'translateX(120%)',
                opacity: visible ? 1 : 0,
                transition: 'transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s ease',
                width: '320px',
            }}
        >
            <div
                className="bg-card border border-border rounded-xl shadow-lg overflow-hidden relative"
                style={{
                    boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
                }}
            >
                {/* Colored left accent bar */}
                <div style={{
                    position: 'absolute',
                    left: 0, top: 0, bottom: 0,
                    width: '4px',
                    background: cfg.color,
                }} />

                <div className="flex items-start gap-3 p-4 pl-5">
                    {/* Icon with soft bg */}
                    <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '8px',
                        background: cfg.bg,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                    }}>
                        <Icon style={{ color: cfg.color, width: '16px', height: '16px' }} />
                    </div>

                    {/* Text */}
                    <div className="flex-1 min-w-0">
                        <p style={{
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: cfg.color,
                            marginBottom: '1px',
                            letterSpacing: '0.02em',
                            textTransform: 'uppercase',
                        }}>
                            {data.title || cfg.title}
                        </p>
                        <p className="text-sm text-foreground leading-tight">
                            {data.message}
                        </p>
                    </div>

                    {/* Close button */}
                    <button
                        onClick={handleClose}
                        className="text-muted-foreground hover:text-foreground transition-colors p-1"
                    >
                        <X style={{ width: '12px', height: '12px' }} />
                    </button>
                </div>

                {/* Progress bar */}
                <div className="h-0.5 bg-muted relative overflow-hidden">
                    <div style={{
                        position: 'absolute',
                        left: 0, top: 0, bottom: 0,
                        width: `${progress}%`,
                        background: cfg.color,
                        opacity: 0.6,
                    }} />
                </div>
            </div>
        </div>
    )
}
