import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class CompetitiveIntelligenceDashboard:
    def __init__(self, data_path='../../Datasets/medicine_data_sampled.csv'):
        self.data = pd.read_csv(data_path)
        self.processed_data = None
        self._preprocess_data()
    
    def _preprocess_data(self):
        self.data['price_numeric'] = self.data['product_price'].str.replace('₹', '').str.replace(',', '').astype(float)
        self.processed_data = self.data[['sub_category', 'product_manufactured', 'price_numeric', 'product_name']].copy()
        self.processed_data = self.processed_data.dropna()
        
        self.processed_data['manufacturer_clean'] = self.processed_data['product_manufactured'].str.strip().str.title()
    
    def market_share_analysis(self):
        
        overall_market_share = self.processed_data['manufacturer_clean'].value_counts()
        overall_market_share_pct = (overall_market_share / len(self.processed_data) * 100).round(2)
        
        category_market_share = {}
        for category in self.processed_data['sub_category'].unique():
            category_data = self.processed_data[self.processed_data['sub_category'] == category]
            market_share = category_data['manufacturer_clean'].value_counts()
            market_share_pct = (market_share / len(category_data) * 100).round(2)
            
            category_market_share[category] = {
                'absolute_share': market_share.to_dict(),
                'percentage_share': market_share_pct.to_dict(),
                'total_products': len(category_data),
                'leading_manufacturer': market_share.index[0] if len(market_share) > 0 else None,
                'herfindahl_index': sum([(share/100)**2 for share in market_share_pct])
            }
        
        manufacturer_categories = self.processed_data.groupby('manufacturer_clean')['sub_category'].nunique().sort_values(ascending=False)
        
        concentration_analysis = {}
        for category in self.processed_data['sub_category'].unique():
            category_data = self.processed_data[self.processed_data['sub_category'] == category]
            manufacturers = category_data['manufacturer_clean'].value_counts()
            
            cr4 = sum(manufacturers.head(4).values) / len(category_data) * 100 if len(manufacturers) >= 4 else 100
            cr8 = sum(manufacturers.head(8).values) / len(category_data) * 100 if len(manufacturers) >= 8 else 100
            
            concentration_analysis[category] = {
                'total_competitors': len(manufacturers),
                'cr4_ratio': round(cr4, 2),
                'cr8_ratio': round(cr8, 2),
                'market_leader_share': round(manufacturers.iloc[0] / len(category_data) * 100, 2) if len(manufacturers) > 0 else 0
            }
        
        return {
            'overall_market_share': overall_market_share_pct.to_dict(),
            'category_market_share': category_market_share,
            'manufacturer_diversification': manufacturer_categories.to_dict(),
            'market_concentration': concentration_analysis
        }
    
    def pricing_strategy_analysis(self):
        """
        Analyze pricing strategies by manufacturer and category
        
        Returns:
            dict: Pricing strategy analysis
        """
        pricing_analysis = {}
        
        manufacturer_pricing = self.processed_data.groupby('manufacturer_clean')['price_numeric'].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ]).round(2)
        manufacturer_pricing['price_range'] = manufacturer_pricing['max'] - manufacturer_pricing['min']
        manufacturer_pricing['coefficient_variation'] = (manufacturer_pricing['std'] / manufacturer_pricing['mean']).round(3)
        
        overall_median_price = self.processed_data['price_numeric'].median()
        manufacturer_pricing['pricing_strategy'] = manufacturer_pricing['median'].apply(
            lambda x: 'Premium' if x > overall_median_price * 1.5 
            else 'Economy' if x < overall_median_price * 0.7 
            else 'Mid-range'
        )
        
        category_pricing = {}
        for category in self.processed_data['sub_category'].unique():
            category_data = self.processed_data[self.processed_data['sub_category'] == category]
            
            if len(category_data) > 0:
                manufacturer_category_pricing = category_data.groupby('manufacturer_clean')['price_numeric'].agg([
                    'count', 'mean', 'median', 'std', 'min', 'max'
                ]).round(2)
                
                category_median = category_data['price_numeric'].median()
                manufacturer_category_pricing['price_position'] = manufacturer_category_pricing['median'].apply(
                    lambda x: 'Above Market' if x > category_median * 1.2
                    else 'Below Market' if x < category_median * 0.8
                    else 'At Market'
                )
                
                category_pricing[category] = manufacturer_category_pricing.to_dict('index')
        
        price_gaps = {}
        for category in self.processed_data['sub_category'].unique():
            category_data = self.processed_data[self.processed_data['sub_category'] == category]
            sorted_prices = sorted(category_data['price_numeric'].unique())
            
            gaps = []
            for i in range(1, len(sorted_prices)):
                gap = sorted_prices[i] - sorted_prices[i-1]
                gap_percentage = (gap / sorted_prices[i-1]) * 100
                if gap_percentage > 25:
                    gaps.append({
                        'lower_price': sorted_prices[i-1],
                        'upper_price': sorted_prices[i],
                        'gap_amount': gap,
                        'gap_percentage': round(gap_percentage, 2)
                    })
            
            price_gaps[category] = gaps
        
        return {
            'manufacturer_pricing_overview': manufacturer_pricing.to_dict('index'),
            'category_pricing_analysis': category_pricing,
            'pricing_gaps': price_gaps
        }
    
    def competitive_positioning_analysis(self):

        positioning_data = []
        
        for manufacturer in self.processed_data['manufacturer_clean'].unique():
            manufacturer_data = self.processed_data[self.processed_data['manufacturer_clean'] == manufacturer]
            
            total_products = len(manufacturer_data)
            categories_served = manufacturer_data['sub_category'].nunique()
            avg_price = manufacturer_data['price_numeric'].mean()
            median_price = manufacturer_data['price_numeric'].median()
            price_range = manufacturer_data['price_numeric'].max() - manufacturer_data['price_numeric'].min()
            
            total_categories = self.processed_data['sub_category'].nunique()
            market_coverage = (categories_served / total_categories) * 100
            
            overall_median = self.processed_data['price_numeric'].median()
            price_premium = (median_price / overall_median - 1) * 100
            
            positioning_data.append({
                'manufacturer': manufacturer,
                'total_products': total_products,
                'categories_served': categories_served,
                'market_coverage_pct': round(market_coverage, 2),
                'avg_price': round(avg_price, 2),
                'median_price': round(median_price, 2),
                'price_range': round(price_range, 2),
                'price_premium_pct': round(price_premium, 2)
            })
        
        positioning_df = pd.DataFrame(positioning_data)
        
        positioning_df['strategic_group'] = 'Niche Player'  # Default
        
        leaders_mask = (positioning_df['market_coverage_pct'] > positioning_df['market_coverage_pct'].quantile(0.75)) & \
                      (positioning_df['total_products'] > positioning_df['total_products'].quantile(0.75))
        positioning_df.loc[leaders_mask, 'strategic_group'] = 'Market Leader'
        
        premium_mask = positioning_df['price_premium_pct'] > 25
        positioning_df.loc[premium_mask, 'strategic_group'] = 'Premium Player'
        
        value_mask = (positioning_df['price_premium_pct'] < -10) & \
                    (positioning_df['total_products'] > positioning_df['total_products'].median())
        positioning_df.loc[value_mask, 'strategic_group'] = 'Value Player'
        
        specialist_mask = (positioning_df['categories_served'] <= 3) & \
                         (positioning_df['total_products'] > positioning_df['total_products'].median())
        positioning_df.loc[specialist_mask, 'strategic_group'] = 'Category Specialist'
        
        return {
            'positioning_matrix': positioning_df.to_dict('records'),
            'strategic_groups': positioning_df['strategic_group'].value_counts().to_dict()
        }
    
    def threat_assessment(self):
        threats_opportunities = {}
        
        pricing_threats = []
        for category in self.processed_data['sub_category'].unique():
            category_data = self.processed_data[self.processed_data['sub_category'] == category]
            category_median = category_data['price_numeric'].median()
            
            aggressive_pricers = category_data[category_data['price_numeric'] < category_median * 0.8]
            
            if not aggressive_pricers.empty:
                for manufacturer in aggressive_pricers['manufacturer_clean'].unique():
                    manufacturer_products = aggressive_pricers[aggressive_pricers['manufacturer_clean'] == manufacturer]
                    avg_discount = ((category_median - manufacturer_products['price_numeric'].mean()) / category_median) * 100
                    
                    pricing_threats.append({
                        'category': category,
                        'manufacturer': manufacturer,
                        'average_discount_pct': round(avg_discount, 2),
                        'products_count': len(manufacturer_products),
                        'threat_level': 'High' if avg_discount > 30 else 'Medium' if avg_discount > 20 else 'Low'
                    })
        
        market_entry_analysis = {}
        for category in self.processed_data['sub_category'].unique():
            category_data = self.processed_data[self.processed_data['sub_category'] == category]
            manufacturers_count = category_data['manufacturer_clean'].nunique()
            
            entry_attractiveness = 'High' if manufacturers_count < 5 else 'Medium' if manufacturers_count < 10 else 'Low'
            
            price_cv = category_data['price_numeric'].std() / category_data['price_numeric'].mean()
            pricing_opportunity = 'High' if price_cv > 0.5 else 'Medium' if price_cv > 0.3 else 'Low'
            
            market_entry_analysis[category] = {
                'current_competitors': manufacturers_count,
                'entry_attractiveness': entry_attractiveness,
                'pricing_opportunity': pricing_opportunity,
                'market_size': len(category_data),
                'price_coefficient_variation': round(price_cv, 3)
            }
        
        consolidation_opportunities = []
        for category in self.processed_data['sub_category'].unique():
            category_data = self.processed_data[self.processed_data['sub_category'] == category]
            market_share = category_data['manufacturer_clean'].value_counts()
            
            small_players = market_share[market_share <= 2]
            
            if len(small_players) >= 3: 
                consolidation_opportunities.append({
                    'category': category,
                    'small_players_count': len(small_players),
                    'total_small_player_products': small_players.sum(),
                    'consolidation_potential': 'High' if len(small_players) >= 5 else 'Medium'
                })
        
        return {
            'pricing_threats': pricing_threats,
            'market_entry_analysis': market_entry_analysis,
            'consolidation_opportunities': consolidation_opportunities
        }
    
    def get_comprehensive_analysis(self):
        return {
            'market_share_analysis': self.market_share_analysis(),
            'pricing_strategy_analysis': self.pricing_strategy_analysis(),
            'competitive_positioning': self.competitive_positioning_analysis(),
            'threat_assessment': self.threat_assessment()
        }


if __name__ == "__main__":
    competitive_dashboard = CompetitiveIntelligenceDashboard()
    
    analysis_results = competitive_dashboard.get_comprehensive_analysis()
    
    print("=== COMPETITIVE INTELLIGENCE DASHBOARD RESULTS ===")
    
    print("\n1. TOP MARKET LEADERS:")
    market_share = analysis_results['market_share_analysis']['overall_market_share']
    for i, (manufacturer, share) in enumerate(list(market_share.items())[:5], 1):
        print(f"{i}. {manufacturer}: {share}% market share")
    
    print("\n2. STRATEGIC GROUPS:")
    strategic_groups = analysis_results['competitive_positioning']['strategic_groups']
    for group, count in strategic_groups.items():
        print(f"{group}: {count} companies")
    
    print("\n3. PRICING THREATS:")
    pricing_threats = analysis_results['threat_assessment']['pricing_threats']
    high_threats = [t for t in pricing_threats if t['threat_level'] == 'High'][:5]
    for i, threat in enumerate(high_threats, 1):
        print(f"{i}. {threat['manufacturer']} in {threat['category']}")
        print(f"   Average discount: {threat['average_discount_pct']}%")
    
    print("\n4. MARKET CONCENTRATION (CR4 Ratio):")
    concentration = analysis_results['market_share_analysis']['market_concentration']
    high_concentration = [(cat, data['cr4_ratio']) for cat, data in concentration.items() if data['cr4_ratio'] > 70]
    high_concentration.sort(key=lambda x: x[1], reverse=True)
    for i, (category, cr4) in enumerate(high_concentration[:5], 1):
        print(f"{i}. {category}: {cr4}% (Top 4 companies)")