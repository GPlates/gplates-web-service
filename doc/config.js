const config = {
  gatsby: {
    pathPrefix: '/',
    siteUrl: 'https://gws.gplates.org',
    gaTrackingId: null,
    trailingSlash: false,
  },
  header: {
    logo: 'https://raw.githubusercontent.com/GPlates/gplates-web-service/master/doc/src/gplates-log.svg',
    logoLink: 'https://gws.gplates.org',
    title:
      `<a href='https://gws.gplates.org/'>GPlates Web Service</a>`,
    githubUrl: 'https://github.com/GPlates/gplates-web-service',
    helpUrl: '',
    tweetText: '',
    social: `<li>
		    <a href="https://twitter.com/earthbytegroup" target="_blank" rel="noopener">
		      <div class="twitterBtn">
		        <img src='https://portal.gplates.org/static/img/twitter-128x128.png' alt={'Twitter'}/>
		      </div>
		    </a>
		  </li>
      <li>
		    <a href="https://www.instagram.com/explore/tags/earthbyte/top/" target="_blank" rel="noopener">
		      <div class="instagramBtn">
		        <img src='http://portal.gplates.org/static/img/instagram-128x128.png' alt={'Discord'}/>
		      </div>
		    </a>
		  </li>
      <li>
		    <a href="https://www.youtube.com/channel/UCa41IQEhmmuXmz9J6iMfsnA" target="_blank" rel="noopener">
		      <div class="youtubeBtn">
		        <img src='http://portal.gplates.org/static/img/youtube-128x128.png' alt={'Discord'}/>
		      </div>
		    </a>
		  </li>
			<li>
		    <a href="https://www.facebook.com/earthbyte" target="_blank" rel="noopener">
		      <div class="facebookBtn">
		        <img src='http://portal.gplates.org/static/img/facebook-128x128.png' alt={'Discord'}/>
		      </div>
		    </a>
		  </li>`,
    links: [{ text: 'AuScope', link: 'https://www.auscope.org.au/' }],
    search: {
      enabled: true,
      indexName: 'test-search',
      algoliaAppId: process.env.GATSBY_ALGOLIA_APP_ID,
      algoliaSearchKey: process.env.GATSBY_ALGOLIA_SEARCH_KEY,
      algoliaAdminKey: process.env.ALGOLIA_ADMIN_KEY,
    },
  },
  sidebar: {
    forcedNavOrder: [
      '/reconstruction', // add trailing slash if enabled above
      '/reconstruction-models',
      '/rotation',
      '/assign-plate-id',
      '/topology',
      '/raster-query',
      '/velocity',
      '/examples',
      '/using-docker'
    ],
    collapsedNav: [
      '/topology', // add trailing slash if enabled above
      '/velocity', // add trailing slash if enabled above
      '/examples',
      '/assign-plate-id',
    ],
    links: [
      { text: 'GPlates', link: 'https://www.gplates.org' }, 
      { text: 'EarthByte', link: 'https://www.earthbyte.org' },
      { text: 'GPlates Portal', link: 'https://portal.gplates.org' }
    ],
    frontline: false,
    ignoreIndex: true,
    title:
      "<a href='https://www.gplates.org/'>GPlates </a><div class='greenCircle'></div><a href='/'>Web Service Doc</a>",
  },
  siteMetadata: {
    title: 'GPlates Web Service',
    description: 'GPlates Web Service Documentation  ',
    ogImage: null,
    docsLocation: 'https://github.com/GPlates/gplates-web-service/blob/master/doc/content',
    favicon: 'https://raw.githubusercontent.com/GPlates/gplates-web-service/master/doc/src/gplates-log.svg',
  },
  pwa: {
    enabled: false, // disabling this will also remove the existing service worker.
    manifest: {
      name: 'GPlates Web Service',
      short_name: 'GWS',
      start_url: '/',
      background_color: '#6b37bf',
      theme_color: '#6b37bf',
      display: 'standalone',
      crossOrigin: 'use-credentials',
      icons: [
        {
          src: 'src/gplates-logo.png',
          sizes: `512x512`,
          type: `image/png`,
        },
      ],
    },
  },
};

module.exports = config;
