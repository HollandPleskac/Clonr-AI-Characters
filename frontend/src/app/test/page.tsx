{
  /* <div id='scrollableDiv' style={{ height: 300, overflow: 'auto' }}>
        <InfiniteScroll
          dataLength={messages.length}
          next={fetchMoreData}
          hasMore={true}
          loader={<h4>Loading...</h4>}
          scrollableTarget='scrollableDiv'
        >
          {messages.map((i, index) => (
            <div className="bg-red-400 border-2 border-white" key={index}>
              div - #{index}
            </div>
          ))}
        </InfiniteScroll>
      </div> */
}

import TestPage from '@/components/TestPage'

export default async function Test() {
  return (
    <div>
      {/* <TopBar /> */}
      <div
        className='bg-gray-900 w-full flex justify-center items-center overflow-hidden'
        style={{ height: 'calc(100vh)' }}
      >
        <TestPage />
      </div>
    </div>
  )
}
