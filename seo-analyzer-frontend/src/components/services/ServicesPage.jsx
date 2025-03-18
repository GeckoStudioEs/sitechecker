import React, { useState, useEffect } from 'react';

const ServicesModule = () => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('link-building');
  const [loading, setLoading] = useState(true);
  
  // Simulate API fetch of service categories
  useEffect(() => {
    // In a real app, this would be an API call
    const fetchCategories = async () => {
      setLoading(true);
      try {
        // Simulated data based on the documentation
        const data = [
          {
            id: 1,
            name: 'Link Building',
            slug: 'link-building',
            description: 'Improve your site authority with quality backlinks',
            icon: '🔗',
            services: [
              {
                id: 1,
                name: 'Guest Posts',
                slug: 'guest-posts',
                description: 'Obtain links from guest post sites',
                benefits: [
                  'Guaranteed organic traffic (500/month)',
                  'Dofollow links (10+)'
                ],
                price: 199,
                price_type: 'fixed'
              },
              {
                id: 2,
                name: 'Niche Edits',
                slug: 'niche-edits',
                description: 'Add links from specific niche websites',
                benefits: [
                  'Guaranteed organic traffic (200/month)',
                  'Dofollow links (5+)'
                ],
                price: 149,
                price_type: 'fixed'
              },
              {
                id: 3,
                name: 'Authority Links',
                slug: 'authority-links',
                description: 'Links from high authority sites',
                benefits: [
                  'Specific organic traffic (500/month)',
                  'Dofollow links (5+)'
                ],
                price: 249,
                price_type: 'fixed'
              },
              {
                id: 4,
                name: 'Homepage Links',
                slug: 'homepage-links',
                description: 'Links from home pages with high authority',
                benefits: [
                  'Organic traffic (50+)',
                  'Dofollow links (5+)'
                ],
                price: 299,
                price_type: 'fixed'
              }
            ]
          },
          {
            id: 2,
            name: 'Keyword Research',
            slug: 'keyword-research',
            description: 'Discover the best keywords for your website',
            icon: '🔍',
            services: [
              {
                id: 5,
                name: 'Keyword Research',
                slug: 'keyword-research',
                description: 'Complete keyword research',
                benefits: [
                  'Top 50 search opportunities',
                  'Intent, CPC and volume analysis'
                ],
                price: 149,
                price_type: 'fixed'
              },
              {
                id: 6,
                name: 'Topical Map',
                slug: 'topical-map',
                description: 'Structured content plan for your website',
                benefits: [
                  'Keyword grouping by topic',
                  'Intent, CPC and volume analysis',
                  'Pillar-based recommendations'
                ],
                price: 199,
                price_type: 'fixed'
              }
            ]
          },
          {
            id: 3,
            name: 'Content Writing',
            slug: 'content-writing',
            description: 'High-quality content for your site',
            icon: '✏️',
            services: [
              {
                id: 7,
                name: 'Website Content',
                slug: 'website-content',
                description: 'Written content for website or blog',
                benefits: [
                  '1000+ word articles',
                  'Multiple languages available',
                  'SEO optimized'
                ],
                price: 0.10,
                price_type: 'per word'
              }
            ]
          },
          {
            id: 4,
            name: 'Web Development',
            slug: 'web-development',
            description: 'Professional web development services',
            icon: '💻',
            services: [
              {
                id: 8,
                name: 'UI/UX Design',
                slug: 'ui-ux-design',
                description: 'User interface design',
                benefits: [
                  'Wireframes, mockups and final designs',
                  'Traffic and conversion optimization',
                  'Responsive'
                ],
                price: 999,
                price_type: 'fixed'
              },
              {
                id: 9,
                name: 'Web Development',
                slug: 'web-development',
                description: 'Complete website development',
                benefits: [
                  'Development from scratch',
                  'SEO optimized',
                  'Integrations and migrations'
                ],
                price: 2499,
                price_type: 'fixed'
              },
              {
                id: 10,
                name: 'Support and Refinements',
                slug: 'support-refinements',
                description: 'Technical support for existing sites',
                benefits: [
                  'Bug and SEO issue fixing',
                  'Security patches',
                  'Protection implementations'
                ],
                price: 99,
                price_type: 'monthly'
              }
            ]
          },
          {
            id: 5,
            name: 'Video Production',
            slug: 'video-production',
            description: 'Professional video creation services',
            icon: '🎬',
            services: [
              {
                id: 11,
                name: 'Product Explainer Video',
                slug: 'product-explainer',
                description: 'Product explainer videos',
                benefits: [
                  'High quality videos',
                  'Professional script',
                  'Clear and concise'
                ],
                price: 799,
                price_type: 'fixed'
              },
              {
                id: 12,
                name: 'Blog to Video',
                slug: 'blog-to-video',
                description: 'Convert articles to videos',
                benefits: [
                  'Created by professionals',
                  'Image design',
                  'Multiple formats'
                ],
                price: 399,
                price_type: 'fixed'
              }
            ]
          },
          {
            id: 6,
            name: 'Website Analytics',
            slug: 'website-analytics',
            description: 'Analytics setup and reporting',
            icon: '📊',
            services: [
              {
                id: 13,
                name: 'Google Analytics + Starter Setup',
                slug: 'ga-setup',
                description: 'Initial analytics configuration',
                benefits: [
                  'Google Tag Manager',
                  'Google Analytics 4',
                  'Custom events'
                ],
                price: 299,
                price_type: 'fixed'
              }
            ]
          },
          {
            id: 7,
            name: 'SEO',
            slug: 'seo',
            description: 'Search Engine Optimization services',
            icon: '🚀',
            services: [
              {
                id: 14,
                name: 'SEO Consultation',
                slug: 'seo-consultation',
                description: 'Personalized SEO consulting',
                benefits: [
                  'Increased search traffic',
                  'Improved conversions',
                  'Better keyword positioning'
                ],
                price: 199,
                price_type: 'hourly'
              }
            ]
          },
          {
            id: 8,
            name: 'UX Research',
            slug: 'ux-research',
            description: 'User experience research services',
            icon: '🧪',
            services: [
              {
                id: 15,
                name: 'UX Website Audit',
                slug: 'ux-website-audit',
                description: 'User experience audit',
                benefits: [
                  'Problem identification',
                  'Improvement opportunities',
                  'Recommendations'
                ],
                price: 599,
                price_type: 'fixed'
              },
              {
                id: 16,
                name: 'UX Content Audit',
                slug: 'ux-content-audit',
                description: 'Content analysis for user experience',
                benefits: [
                  'Existing content review',
                  'Structural recommendations',
                  'Content improvements'
                ],
                price: 499,
                price_type: 'fixed'
              },
              {
                id: 17,
                name: 'UX Keyword & CRO Audit',
                slug: 'ux-keyword-cro-audit',
                description: 'Analysis for conversion improvement',
                benefits: [
                  'Search intent analysis',
                  'Specific SEO/CRO strategies',
                  'Google Analytics integration'
                ],
                price: 699,
                price_type: 'fixed'
              }
            ]
          }
        ];
        
        setCategories(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching service categories:', error);
        setLoading(false);
      }
    };
    
    fetchCategories();
  }, []);
  
  const handleServiceRequest = (serviceId) => {
    // In a real app, this would navigate to a service request form
    // or open a modal for requesting the service
    alert(`Service requested: ${serviceId}`);
  };
  
  // Helper function to format price
  const formatPrice = (price, priceType) => {
    if (priceType === 'fixed') {
      return `$${price}`;
    } else if (priceType === 'hourly') {
      return `$${price}/hour`;
    } else if (priceType === 'monthly') {
      return `$${price}/month`;
    } else if (priceType === 'per word') {
      return `$${price}/word`;
    }
    return `$${price}`;
  };
  
  // Find the selected category
  const currentCategory = categories.find(cat => cat.slug === selectedCategory) || {};
  
  return (
    <div className="w-full max-w-6xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Our Services</h1>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* Service Categories Sidebar */}
        <div className="md:w-1/4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="p-4 border-b">
              <h2 className="text-xl font-semibold">Categories</h2>
            </div>
            <div className="p-4">
              <div className="flex flex-col space-y-2">
                {loading ? (
                  <div>Loading categories...</div>
                ) : (
                  categories.map(category => (
                    <button
                      key={category.id}
                      className={`text-left p-2 rounded-md ${selectedCategory === category.slug ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}
                      onClick={() => setSelectedCategory(category.slug)}
                    >
                      <span className="mr-2">{category.icon}</span>
                      {category.name}
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Services List */}
        <div className="md:w-3/4">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-lg">Loading services...</div>
            </div>
          ) : (
            <div>
              <h2 className="text-2xl font-bold mb-4">{currentCategory.name}</h2>
              <p className="text-gray-600 mb-6">{currentCategory.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {currentCategory.services?.map(service => (
                  <div key={service.id} className="bg-white rounded-lg shadow flex flex-col h-full">
                    <div className="p-4 border-b">
                      <div className="flex justify-between items-start">
                        <h3 className="text-xl font-semibold">{service.name}</h3>
                        <span className="inline-block bg-gray-100 text-gray-800 text-sm px-2 py-1 rounded">
                          {formatPrice(service.price, service.price_type)}
                        </span>
                      </div>
                    </div>
                    <div className="p-4 flex-grow">
                      <p className="text-gray-600 mb-4">{service.description}</p>
                      <div>
                        <h4 className="font-medium mb-2">Benefits:</h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {service.benefits.map((benefit, index) => (
                            <li key={index} className="text-gray-700">{benefit}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="p-4 border-t">
                      <button 
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded" 
                        onClick={() => handleServiceRequest(service.id)}
                      >
                        Request Service
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ServicesModule;