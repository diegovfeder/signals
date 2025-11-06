'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'

type ConfirmStatus = 'loading' | 'success' | 'error'

interface ConfirmResponse {
  message: string
  email: string
}

interface ErrorResponse {
  detail: string
}

export default function ConfirmEmailPage() {
  const params = useParams()
  const router = useRouter()
  const [status, setStatus] = useState<ConfirmStatus>('loading')
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    const confirmEmail = async () => {
      const token = params.token as string

      if (!token) {
        setStatus('error')
        setMessage('Invalid confirmation link')
        return
      }

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(
          `${apiUrl}/api/subscribe/confirm/${token}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          },
        )

        const data = await response.json()

        if (response.ok) {
          const confirmData = data as ConfirmResponse
          setStatus('success')
          setMessage(confirmData.message)
          setEmail(confirmData.email)
          // Redirect to dashboard after 3 seconds
          setTimeout(() => router.push('/dashboard'), 3000)
        } else {
          const errorData = data as ErrorResponse
          setStatus('error')
          setMessage(errorData.detail || 'Confirmation failed')
        }
      } catch (error) {
        setStatus('error')
        setMessage('Network error. Please try again.')
        console.error('[confirm] Error:', error)
      }
    }

    confirmEmail()
  }, [params.token, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full">
        {status === 'loading' && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              Confirming your email...
            </h1>
            <p className="text-gray-600">Please wait a moment</p>
          </div>
        )}

        {status === 'success' && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="bg-green-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <svg
                className="h-10 w-10 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Email Confirmed!
            </h1>
            <p className="text-gray-700 mb-4">{message}</p>
            {email && (
              <p className="text-sm text-gray-600 mb-4">
                Confirmed email: <span className="font-medium">{email}</span>
              </p>
            )}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                Redirecting to dashboard in 3 seconds...
              </p>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="bg-red-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <svg
                className="h-10 w-10 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Confirmation Failed
            </h1>
            <p className="text-gray-700 mb-6">{message}</p>
            <button
              onClick={() => router.push('/')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Go to Home
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
