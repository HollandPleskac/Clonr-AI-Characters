'use client'
import { ClonesService, CloneSortType } from "@/client"

export default function Test() {

  async function getClones() {
   const clones = await ClonesService.queryClonesClonesGet()
   console.log(clones)
  }

  return (
    <div>
      <h1 className="text-white" >TEST</h1>
      <button className="text-white" onClick={getClones}  >CLICK ME</button>
    </div>
  )
}
