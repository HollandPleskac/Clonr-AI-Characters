import HomePage from '@/components/HomePage'
import PlusModal from '@/components/PlusModal'

async function fetchCharacters() {
  return [
    {
      id: '298618',
      name: 'The Flash',
      rating: 6.9,
      short_description:
        "When his attempt to save his family inadvertently alters the future, Barry Allen becomes trapped in a reality in which General Zod has returned and there are no Super Heroes to turn to. In order to save the world that he is in and return to the future that he knows, Barry's only hope is to race for his life. But will making the ultimate sacrifice be enough to reset the universe?",
      poster: 'https://image.tmdb.org/t/p/w500/rktDFPbfHfUbArZ6OOOKsXcv0Bm.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/yF1eOkaYvwiORauRCPWznV9xVvi.jpg',
      tags: [
        {
          name: 'Action',
        },
        {
          name: 'Adventure',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '346698',
      name: 'Barbie',
      rating: 7.6,
      short_description:
        'Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land. However, when they get a chance to go to the real world, they soon discover the joys and perils of living among humans.',
      poster: 'https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/ctMserH8g2SeOAnCw5gFjdQF8mo.jpg',
      tags: [
        {
          name: 'Adventure',
        },
        {
          name: 'Comedy',
        },
        {
          name: 'Fantasy',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '667538',
      name: 'Transformers: Rise of the Beasts',
      rating: 7.5,
      short_description:
        'When a new threat capable of destroying the entire planet emerges, Optimus Prime and the Autobots must team up with a powerful faction known as the Maximals. With the fate of humanity hanging in the balance, humans Noah and Elena will do whatever it takes to help the Transformers as they engage in the ultimate battle to save Earth.',
      poster: 'https://image.tmdb.org/t/p/w500/gPbM0MK8CP8A174rmUwGsADNYKD.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/2vFuG6bWGyQUzYS9d69E5l85nIz.jpg',
      tags: [
        {
          name: 'Action',
        },
        {
          name: 'Adventure',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '447277',
      name: 'The Little Mermaid',
      rating: 6.4,
      short_description:
        'The youngest of King Triton’s daughters, and the most defiant, Ariel longs to find out more about the world beyond the sea, and while visiting the surface, falls for the dashing Prince Eric. With mermaids forbidden to interact with humans, Ariel makes a deal with the evil sea witch, Ursula, which gives her a chance to experience life on land, but ultimately places her life – and her father’s crown – in jeopardy.',
      poster: 'https://image.tmdb.org/t/p/w500/ym1dxyOk4jFcSl4Q2zmRrA5BEEN.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/znUYFf0Sez5lUmxPr3Cby7TVJ6c.jpg',
      tags: [
        {
          name: 'Adventure',
        },
        {
          name: 'Family',
        },
        {
          name: 'Fantasy',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '976573',
      name: 'Elemental',
      rating: 7.6,
      short_description:
        'In a city where fire, water, land and air residents live together, a fiery young woman and a go-with-the-flow guy will discover something elemental: how much they have in common.',
      poster: 'https://image.tmdb.org/t/p/w500/8riWcADI1ekEiBguVB9vkilhiQm.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/cSYLX73WskxCgvpN3MtRkYUSj1T.jpg',
      tags: [
        {
          name: 'Animation',
        },
        {
          name: 'Comedy',
        },
        {
          name: 'Family',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '4443233434',
      name: 'God Is a Bullet',
      rating: 6.2,
      short_description:
        'Based on true events and the novel of the same name. Vice detective Bob Hightower finds his ex-wife murdered and daughter kidnapped by a cult. Frustrated by the botched official investigations, he quits the force and infiltrates the cult to hunt down the leader with the help of the cult’s only female victim escapee, Case Hardin.',
      poster: 'https://image.tmdb.org/t/p/w500/5kiLS9nsSJxDdlYUyYGiSUt8Fi8.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/hjyqNFHx5wIO8dqaRi0v2ix1wiR.jpg',
      tags: [
        {
          name: 'Action',
        },
        {
          name: 'Crime',
        },
        {
          name: 'Horror',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '121353333333',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '5532235',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '352342342355',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '444234',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '234324',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '45435435',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '2345234532464326',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '435435',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '1345435',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '234',
      name: 'Bird Box Barcelona',
      rating: 6.1,
      short_description:
        'After a mysterious force decimates the world’s population, Sebastian must navigate his own survival journey through the desolate streets of Barcelona. As he forms uneasy alliances with other survivors and they try to escape the city, an unexpected and even more sinister threat grows.',
      poster: 'https://image.tmdb.org/t/p/w500/hOb6ODI7QQFKkOe3eJU2Fdh2fk1.jpg',
      avatar_uri:
        'https://image.tmdb.org/t/p/original/tmDdFWtXwq7alX2dPG3LPPNNVs2.jpg',
      tags: [
        {
          name: 'Drama',
        },
        {
          name: 'Horror',
        },
        {
          name: 'Science Fiction',
        },
      ],
      num_messages: 2400,
      num_conversations: 1032,
      creator_id: '233523',
      created_at: new Date(),
      updated_at: new Date()
    },
  ]
}

export default async function Home() {
  const [topCharacters, continueChatting, trending, anime] = await Promise.all([
    fetchCharacters(),
    fetchCharacters(),
    fetchCharacters(),
    fetchCharacters(),
  ])

  return (
    <main className='w-full flex flex-col h-full'>
      <HomePage
        topCharacters={topCharacters}
        continueChatting={continueChatting}
        trending={trending}
        anime={anime}
      />
      <PlusModal />
    </main>
  )
}
