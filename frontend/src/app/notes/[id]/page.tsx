async function getNote(noteId: string) {
  return noteId
}

export default async function NotesPage({ params }: any) {
  const note = await getNote(params.id)
  return (
    <main className='w-full h-screen bg-slate-500'>
      <h1>note {note}</h1>
    </main>
  )
}
