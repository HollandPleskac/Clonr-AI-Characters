'use client'

import { useEffect } from "react"


export default function GlobalError({
    error,
    reset,
}: {
    error: Error
    reset: () => void
}) {
    useEffect(() => {
        // Log the error to an error reporting service
        console.error(error)
    }, [error])

    return (
        <div className="h-screen text-white flex flex-col justify-center items-center" >
                <h2 className="text-lg mb-2" >Something went wrong!</h2>
                <button onClick={() => reset()}>Try again</button>
        </div>
    )
}