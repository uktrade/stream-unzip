import { govukEleventyPlugin } from '@x-govuk/govuk-eleventy-plugin'
import fs from 'fs';

export default function(eleventyConfig) {
  // Register the plugin
  eleventyConfig.addPlugin(govukEleventyPlugin, {
    icons: {
      shortcut: '/assets/dit-favicon.png'
    },
    header: {
      logotype: {
        html: fs.readFileSync('./docs/assets/dit-logo.svg', {encoding: 'utf8'})
      },
      productName: 'stream-unzip',
    },
    footer: {
      meta: {
        items: [
          {
            href: 'https://github.com/uktrade/stream-unzip',
            text: 'GitHub repository for stream-unzip'
          },
          {
            href: 'https://www.gov.uk/government/organisations/department-for-business-and-trade',
            text: 'Created by the Department for Business and Trade (DBT)'
          }
        ]
      }
    },
    stylesheets: ['/assets/styles.css'],
  })

  eleventyConfig.addPassthroughCopy('./docs/assets')
  eleventyConfig.addPassthroughCopy('./docs/CNAME')

  return {
    dataTemplateEngine: 'njk',
    htmlTemplateEngine: 'njk',
    markdownTemplateEngine: 'njk',
    dir: {
      // Use layouts from the plugin
      input: 'docs',
    }
  }
};
