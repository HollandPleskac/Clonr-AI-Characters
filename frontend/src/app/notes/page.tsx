import Image from 'next/image'

//if not using fetch then change caching behavior and runtime
// get Server Side Props
export const dynamic = 'auto',
  dynamicParams = 'true',
  revalidate = 0,
  fetchCache = 'auto',
  runtime = 'nodejs',
  preferredRegion = 'auto'

async function getNotes() {
  return ['note1', 'notes2', 'notes3']
  // ==getServerSideProps: if using fetch pass {cache: 'no-store' } to refetch items on every request (otherwise nextjs caches the route)
}

export default async function NotesPage() {
  const notes = await getNotes()
  return (
    <main className='w-full h-screen bg-slate-500'>
      <h1 className='bg-red-400'>test</h1>
      {notes.map((note) => {
        return (
          <div key={note}>
            <h1 className='text-white'>{note}</h1>
          </div>
        )
      })}
    </main>
  )
}
