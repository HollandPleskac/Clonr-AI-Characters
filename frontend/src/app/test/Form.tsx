'use client'

import { useEffect, useState } from 'react'
import CharactersSidebar from '@/components/ChatPage/Characters/Sidebar'
import Chat from '@/components/ChatPage/Chat';
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination';
import useConversations from '@/hooks/useConversations';
import { AdaptationStrategy, InformationStrategy, MemoryStrategy } from '@/client';
import axios from 'axios';




interface FormProps {
    handleShowChat: (cloneId: string, convId: string) => void;
    llmStart: string;
    setLlmStart: React.Dispatch<React.SetStateAction<string>>;
    characterName: string;
    setCharacterName: React.Dispatch<React.SetStateAction<string>>;
    username: string;
    setUsername: React.Dispatch<React.SetStateAction<string>>;
    shortDescription: string;
    setShortDescription: React.Dispatch<React.SetStateAction<string>>;
    longDescription: string;
    setLongDescription: React.Dispatch<React.SetStateAction<string>>;
    selectedFile: File | null;
    setSelectedFile: any;
    imageSrc: string;
    setImageSrc: React.Dispatch<React.SetStateAction<string>>;
    session: any
}




const Form: React.FC<FormProps> = ({
    handleShowChat,
    llmStart,
    setLlmStart,
    characterName,
    setCharacterName,
    username,
    setUsername,
    shortDescription,
    setShortDescription,
    longDescription,
    setLongDescription,
    selectedFile,
    setSelectedFile,
    imageSrc,
    setImageSrc,
    session
}) => {



    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.size <= 10 * 1024 * 1024) { // Limit to 10MB
            setSelectedFile(file);

            // Create a new FileReader object
            const reader = new FileReader();

            // Register load event handler
            reader.onload = (e) => {
                setImageSrc(e.target.result);
            };

            // Start reading the file as Data URL so we can display it
            reader.readAsDataURL(file);
        } else {
            alert("File size should not exceed 10MB.");
        }
    };

    async function createChar(e) {
        e.preventDefault()
        // register user as creator
        const reqBody = {
            "email": session.user.email,
            "nsfw": true,
            "personal": true,
            "quality": true,
            "story": true,
            "roleplay": true
        };

        const res = await axios.post('http://localhost:8000/signup/creators', reqBody, {
            withCredentials: true,
        });
        console.log("registered user as creator")

        // create character
        const requestBody = {
            "name": "string",
            "short_description": "string",
            "long_description": "stringstringstringstringstringst",
            "greeting_message": "string",
            "avatar_uri": "string",
            "is_active": true,
            "is_public": false,
            "is_short_description_public": true,
            "is_long_description_public": false,
            "is_greeting_message_public": true,
            "tags": [0]
        };

        const response = await axios.post('http://localhost:8000/clones', requestBody, {
            withCredentials: true
        });
        console.log("created a character",response.data)
        // create conversation
        // const convId = await createCharacterConversation("131b7003-a164-413d-b402-a84dd3cc79fc", 'ZERO') // try "LONG_TERM"
        // console.log("created a conversation")
        // handleShowChat("131b7003-a164-413d-b402-a84dd3cc79fc", convId)
    }


    const { createConversation } = useConversations();

    async function createCharacterConversation(
        characterId: string,
        memoryStrategy: string,
        informationStrategy: string = 'INTERNAL',
        adaptationStrategy: string = 'ZERO',
    ) {
        const conversationData = {
            name: 'Test Conversation',
            user_name: username,
            memory_strategy: MemoryStrategy[memoryStrategy],
            information_strategy: InformationStrategy[informationStrategy],
            adaptation_strategy: AdaptationStrategy[adaptationStrategy],
            clone_id: characterId,
        }
        console.log("conv data", conversationData)
        const conversationId = await createConversation(conversationData)
        return conversationId
    }


    return (
        <div className='bg-white px-10 py-10' >
            <form>
                <div className="space-y-12">
                    <div className="border-b border-gray-900/10 pb-12">
                        <h2 className="text-base font-semibold leading-7 text-gray-900">Create Character Zero Memory</h2>
                        <p className="mt-1 text-sm leading-6 text-gray-600">Test character by clicking the "create" button below</p>

                        <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
                            <div className="sm:col-span-4">
                                <label htmlFor="llm" className="block text-sm font-medium leading-6 text-gray-900">LLM system start </label>
                                <div className="mt-2">
                                    <div className="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                                        <input value={llmStart} onChange={(e) => setLlmStart(e.target.value)} type="text" name="username" id="llm" className="pl-3 block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="You are a character and are doing a roleplay..." />
                                    </div>
                                </div>
                            </div>

                            <div className="sm:col-span-4">
                                <label htmlFor="charname" className="block text-sm font-medium leading-6 text-gray-900">Character Name</label>
                                <div className="mt-2">
                                    <div className="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                                        <input value={characterName} onChange={(e) => setCharacterName(e.target.value)} type="text" name="username" id="charname" className="pl-3 block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="Miles Moralis" />
                                    </div>
                                </div>
                            </div>

                            <div className="sm:col-span-4">
                                <label htmlFor="username" className="block text-sm font-medium leading-6 text-gray-900">Username</label>
                                <div className="mt-2">
                                    <div className="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                                        <input value={username} onChange={(e) => setUsername(e.target.value)} type="text" name="username" id="username" className="pl-3 block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                                    </div>
                                </div>
                            </div>

                            <div className="col-span-full">
                                <label htmlFor="shortDesc" className="block text-sm font-medium leading-6 text-gray-900">Short Description</label>
                                <div className="mt-2">
                                    <textarea value={shortDescription} onChange={(e) => setShortDescription(e.target.value)} id="shortDesc" name="about" rows={3} className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>
                                </div>
                                <p className="mt-3 text-sm leading-6 text-gray-600">Write a brief overview of the character</p>
                            </div>

                            <div className="col-span-full">
                                <label htmlFor="longDesc" className="block text-sm font-medium leading-6 text-gray-900">Long Description</label>
                                <div className="mt-2">
                                    <textarea value={longDescription} onChange={(e) => setLongDescription(e.target.value)} id="longDesc" name="about" rows={3} className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>
                                </div>
                                <p className="mt-3 text-sm leading-6 text-gray-600">Write a detailed description of the character</p>
                            </div>

                            {/* <div className="col-span-full">
                                <label htmlFor="photo" className="block text-sm font-medium leading-6 text-gray-900">Photo</label>
                                <div className="mt-2 flex items-center gap-x-3">
                                    <svg className="h-12 w-12 text-gray-300" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                                        <path fill-rule="evenodd" d="M18.685 19.097A9.723 9.723 0 0021.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 003.065 7.097A9.716 9.716 0 0012 21.75a9.716 9.716 0 006.685-2.653zm-12.54-1.285A7.486 7.486 0 0112 15a7.486 7.486 0 015.855 2.812A8.224 8.224 0 0112 20.25a8.224 8.224 0 01-5.855-2.438zM15.75 9a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" clip-rule="evenodd" />
                                    </svg>
                                    <button type="button" className="rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">Change</button>
                                </div>
                            </div> */}

                            <div className="col-span-full">
                                <label htmlFor="cover-photo" className="block text-sm font-medium leading-6 text-gray-900">Cover photo</label>
                                <div className="mt-2 flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10">

                                    <div className="text-center">
                                        <svg className="mx-auto h-12 w-12 text-gray-300" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                                            {/* SVG Path here */}
                                        </svg>
                                        <div className="mt-4 flex text-sm leading-6 text-gray-600">
                                            <label htmlFor="file-upload" className="relative cursor-pointer rounded-md bg-white font-semibold text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 hover:text-indigo-500">
                                                <span>Upload a file</span>
                                                <input id="file-upload" name="file-upload" type="file" className="sr-only" onChange={handleFileChange} />
                                            </label>
                                            <p className="pl-1">or drag and drop</p>
                                        </div>
                                        <p className="text-xs leading-5 text-gray-600">PNG, JPG, GIF up to 10MB</p>
                                    </div>
                                </div>
                            </div>
                            {imageSrc && (
                                <img src={imageSrc} alt="Uploaded preview" className="border-2 border-black object-cover w-full h-full rounded-lg aspect-[16/9]" />
                            )}
                        </div>
                    </div>

                    {/* <div className="border-b border-gray-900/10 pb-12">
                        <h2 className="text-base font-semibold leading-7 text-gray-900">Personal Information</h2>
                        <p className="mt-1 text-sm leading-6 text-gray-600">Use a permanent address where you can receive mail.</p>

                        <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
                            <div className="sm:col-span-3">
                                <label htmlFor="first-name" className="block text-sm font-medium leading-6 text-gray-900">First name</label>
                                <div className="mt-2">
                                    <input type="text" name="first-name" id="first-name" className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                                </div>
                            </div>

                            <div className="sm:col-span-3">
                                <label htmlFor="last-name" className="block text-sm font-medium leading-6 text-gray-900">Last name</label>
                                <div className="mt-2">
                                    <input type="text" name="last-name" id="last-name" className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                                </div>
                            </div>

                            <div className="sm:col-span-4">
                                <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">Email address</label>
                                <div className="mt-2">
                                    <input id="email" name="email" type="email" className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                                </div>
                            </div>

                            <div className="sm:col-span-3">
                                <label htmlFor="country" className="block text-sm font-medium leading-6 text-gray-900">Country</label>
                                <div className="mt-2">
                                    <select id="country" name="country" className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6">
                                        <option>United States</option>
                                        <option>Canada</option>
                                        <option>Mexico</option>
                                    </select>
                                </div>
                            </div>

                            <div className="col-span-full">
                                <label htmlFor="street-address" className="block text-sm font-medium leading-6 text-gray-900">Street address</label>
                                <div className="mt-2">
                                    <input type="text" name="street-address" id="street-address" className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                                </div>
                            </div>

                            <div className="sm:col-span-2 sm:col-start-1">
                                <label htmlFor="city" className="block text-sm font-medium leading-6 text-gray-900">City</label>
                                <div className="mt-2">
                                    <input type="text" name="city" id="city" className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                                </div>
                            </div>

                            <div className="sm:col-span-2">
                                <label htmlFor="region" className="block text-sm font-medium leading-6 text-gray-900">State / Province</label>
                                <div className="mt-2">
                                    <input type="text" name="region" id="region" className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                                </div>
                            </div>

                            <div className="sm:col-span-2">
                                <label htmlFor="postal-code" className="block text-sm font-medium leading-6 text-gray-900">ZIP / Postal code</label>
                                <div className="mt-2">
                                    <input type="text" name="postal-code" id="postal-code" className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                                </div>
                            </div>
                        </div>
                    </div> */}

                    {/* <div className="border-b border-gray-900/10 pb-12">
                        <h2 className="text-base font-semibold leading-7 text-gray-900">Notifications</h2>
                        <p className="mt-1 text-sm leading-6 text-gray-600">We'll always let you know about important changes, but you pick what else you want to hear about.</p>

                        <div className="mt-10 space-y-10">
                            <fieldset>
                                <legend className="text-sm font-semibold leading-6 text-gray-900">By Email</legend>
                                <div className="mt-6 space-y-6">
                                    <div className="relative flex gap-x-3">
                                        <div className="flex h-6 items-center">
                                            <input id="comments" name="comments" type="checkbox" className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600" />
                                        </div>
                                        <div className="text-sm leading-6">
                                            <label htmlFor="comments" className="font-medium text-gray-900">Comments</label>
                                            <p className="text-gray-500">Get notified when someones posts a comment on a posting.</p>
                                        </div>
                                    </div>
                                    <div className="relative flex gap-x-3">
                                        <div className="flex h-6 items-center">
                                            <input id="candidates" name="candidates" type="checkbox" className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600" />
                                        </div>
                                        <div className="text-sm leading-6">
                                            <label htmlFor="candidates" className="font-medium text-gray-900">Candidates</label>
                                            <p className="text-gray-500">Get notified when a candidate applies for a job.</p>
                                        </div>
                                    </div>
                                    <div className="relative flex gap-x-3">
                                        <div className="flex h-6 items-center">
                                            <input id="offers" name="offers" type="checkbox" className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600" />
                                        </div>
                                        <div className="text-sm leading-6">
                                            <label htmlFor="offers" className="font-medium text-gray-900">Offers</label>
                                            <p className="text-gray-500">Get notified when a candidate accepts or rejects an offer.</p>
                                        </div>
                                    </div>
                                </div>
                            </fieldset>
                            <fieldset>
                                <legend className="text-sm font-semibold leading-6 text-gray-900">Push Notifications</legend>
                                <p className="mt-1 text-sm leading-6 text-gray-600">These are delivered via SMS to your mobile phone.</p>
                                <div className="mt-6 space-y-6">
                                    <div className="flex items-center gap-x-3">
                                        <input id="push-everything" name="push-notifications" type="radio" className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-600" />
                                        <label htmlFor="push-everything" className="block text-sm font-medium leading-6 text-gray-900">Everything</label>
                                    </div>
                                    <div className="flex items-center gap-x-3">
                                        <input id="push-email" name="push-notifications" type="radio" className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-600" />
                                        <label htmlFor="push-email" className="block text-sm font-medium leading-6 text-gray-900">Same as email</label>
                                    </div>
                                    <div className="flex items-center gap-x-3">
                                        <input id="push-nothing" name="push-notifications" type="radio" className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-600" />
                                        <label htmlFor="push-nothing" className="block text-sm font-medium leading-6 text-gray-900">No push notifications</label>
                                    </div>
                                </div>
                            </fieldset>
                        </div>
                    </div> */}
                </div>

                <div className="mt-6 flex items-center justify-end gap-x-6">
                    {/* <button type="button" className="text-sm font-semibold leading-6 text-gray-900">Cancel</button> */}
                    <button onClick={createChar} className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Create</button>
                </div>
            </form>

        </div>
    )
}

export default Form