import { SignIn } from '@clerk/nextjs'
import React from 'react'

const signIn = () => {
  return (
    <main className='flex justify-center items-center h-screen bg-[#1C1F2E]'>
        <SignIn >
        </SignIn>
    </main>
  )
}

export default signIn