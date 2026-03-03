'use client'

import { createContext, useContext, useState, useCallback, useRef } from 'react'
import Toast, { ToastData } from './Toast'

interface ToastContextValue {
    toast: {
        success: (message: string, title?: string) => void
        error: (message: string, title?: string) => void
        warning: (message: string, title?: string) => void
        info: (message: string, title?: string) => void
    }
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
    const [toasts, setToasts] = useState<ToastData[]>([])
    const counterRef = useRef(0)

    const addToast = useCallback((
        type: ToastData['type'],
        message: string,
        title?: string
    ) => {
        const id = ++counterRef.current
        setToasts(prev => [...prev, { id, type, message, title }])
    }, [])

    const removeToast = useCallback((id: number) => {
        setToasts(prev => prev.filter(t => t.id !== id))
    }, [])

    const toast = {
        success: (message: string, title?: string) => addToast('success', message, title),
        error: (message: string, title?: string) => addToast('error', message, title),
        warning: (message: string, title?: string) => addToast('warning', message, title),
        info: (message: string, title?: string) => addToast('info', message, title),
    }

    return (
        <ToastContext.Provider value={{ toast }}>
            {children}
            {/* Toast container */}
            <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3 pointer-events-none">
                {toasts.map(t => (
                    <Toast key={t.id} data={t} onClose={removeToast} />
                ))}
            </div>
        </ToastContext.Provider>
    )
}

export function useToast(): ToastContextValue {
    const ctx = useContext(ToastContext)
    if (!ctx) throw new Error('useToast must be used within a ToastProvider')
    return ctx
}
