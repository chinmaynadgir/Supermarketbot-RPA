"""
Real-time Dashboard with Interactive Analytics
"""
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import logging
 
from billing_service import BillingService
from inventory_service import InventoryService

logger = logging.getLogger(__name__)


class RealTimeDashboard:
    """Real-time dashboard with interactive charts and analytics"""
    
    def __init__(
        self,
        parent,
        billing_service: BillingService,
        inventory_service: InventoryService,
    ):
        self.parent = parent
        self.billing_service = billing_service
        self.inventory_service = inventory_service
        
        # Data for charts
        self.sales_data = []
        self.inventory_data = {}
        self.customer_data = {}
        
        self.setup_dashboard()
        self.load_initial_data()
    
    def setup_dashboard(self):
        """Setup the dashboard interface"""
        # Main dashboard frame
        self.dashboard_frame = ttk.Frame(self.parent)
        self.dashboard_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top metrics row
        self.create_metrics_row()
        
        # Charts row
        self.create_charts_row()
        
        # Bottom analytics row
        self.create_analytics_row()
    
    def create_metrics_row(self):
        """Create the top metrics row"""
        metrics_frame = ttk.LabelFrame(
            self.dashboard_frame, text="Live Metrics", padding=10
        )
        metrics_frame.pack(fill='x', pady=(0, 10))
        
        # Create metric cards
        self.create_metric_card(metrics_frame, "Today's Sales", "$0.00", 0, 0)
        self.create_metric_card(metrics_frame, "Total Bills", "0", 0, 1)
        self.create_metric_card(metrics_frame, "Low Stock Items", "0", 0, 2)
        self.create_metric_card(
            metrics_frame, "Inventory Value", "$0.00", 0, 3
        )
        self.create_metric_card(metrics_frame, "Top Product", "N/A", 0, 4)
        self.create_metric_card(metrics_frame, "Avg Bill Value", "$0.00", 0, 5)
    
    def create_metric_card(self, parent, title, value, row, col):
        """Create a metric card"""
        card_frame = ttk.Frame(parent)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        title_label = ttk.Label(
            card_frame, text=title, font=('Arial', 10, 'bold')
        )
        title_label.pack()
        
        value_label = ttk.Label(
            card_frame,
            text=value,
            font=('Arial', 16, 'bold'),
            foreground='#2E8B57',
        )
        value_label.pack()
        
        # Store reference for updates
        attr_name = title.lower().replace(' ', '_').replace("'", '') + "_label"
        setattr(self, attr_name, value_label)
    
    def create_charts_row(self):
        """Create the charts row"""
        charts_frame = ttk.Frame(self.dashboard_frame)
        charts_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Sales chart
        sales_chart_frame = ttk.LabelFrame(
            charts_frame, text="Sales Trend (Last 7 Days)", padding=5
        )
        sales_chart_frame.pack(
            side='left', fill='both', expand=True, padx=(0, 5)
        )
        
        # Use a Figure with constrained_layout to let Matplotlib handle spacing
        self.sales_fig = Figure(figsize=(6, 4), constrained_layout=True)
        self.sales_ax = self.sales_fig.add_subplot(111)
        self.sales_canvas = FigureCanvasTkAgg(self.sales_fig, sales_chart_frame)
        self.sales_canvas.get_tk_widget().pack(fill='both', expand=True)
        # Redraw on resize so the canvas can reflow
        sales_chart_frame.bind("<Configure>", lambda e: self.sales_canvas.draw_idle())
        
        # Inventory chart
        inventory_chart_frame = ttk.LabelFrame(
            charts_frame, text="Inventory Status", padding=5
        )
        inventory_chart_frame.pack(
            side='right', fill='both', expand=True, padx=(5, 0)
        )
        
        self.inventory_fig = Figure(figsize=(6, 4), constrained_layout=True)
        self.inventory_ax = self.inventory_fig.add_subplot(111)
        self.inventory_canvas = FigureCanvasTkAgg(self.inventory_fig, inventory_chart_frame)
        self.inventory_canvas.get_tk_widget().pack(fill='both', expand=True)
        inventory_chart_frame.bind("<Configure>", lambda e: self.inventory_canvas.draw_idle())
    
    def create_analytics_row(self):
        """Create the bottom analytics row"""
        analytics_frame = ttk.LabelFrame(
            self.dashboard_frame, text="Advanced Analytics", padding=10
        )
        analytics_frame.pack(fill='x')
        
        # Create tabs for different analytics
        self.analytics_notebook = ttk.Notebook(analytics_frame)
        self.analytics_notebook.pack(fill='both', expand=True)
        
        # Customer analytics tab
        self.create_customer_analytics_tab()
        
        # Product performance tab
        self.create_product_analytics_tab()
        
        # Predictive analytics tab
        self.create_predictive_analytics_tab()
    
    def create_customer_analytics_tab(self):
        """Create customer analytics tab"""
        customer_frame = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(customer_frame, text="Customer Insights")
        
        # Customer metrics
        metrics_text = tk.Text(customer_frame, height=8, width=80)
        metrics_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.customer_metrics_text = metrics_text
    
    def create_product_analytics_tab(self):
        """Create product performance tab"""
        product_frame = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(product_frame, text="Product Performance")
        
        # Product performance metrics
        product_text = tk.Text(product_frame, height=8, width=80)
        product_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.product_metrics_text = product_text
    
    def create_predictive_analytics_tab(self):
        """Create predictive analytics tab"""
        predictive_frame = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(predictive_frame, text="Predictions")

        # Predictions (placeholder)
        ai_text = tk.Text(predictive_frame, height=8, width=80)
        ai_text.pack(fill='both', expand=True, padx=5, pady=5)

        self.ai_predictions_text = ai_text
    
    def load_initial_data(self):
        """Load initial data and update dashboard"""
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update all dashboard components"""
        try:
            self.update_metrics()
            self.update_sales_chart()
            self.update_inventory_chart()
            self.update_analytics()
            
            # Schedule next update (every 5 seconds)
            self.parent.after(5000, self.update_dashboard)
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
    
    def update_metrics(self):
        """Update the metrics cards"""
        try:
            # Get today's data
            today = datetime.now()
            today_summary = self.billing_service.get_daily_sales_summary(today)
            
            # Get inventory summary
            inventory_summary = self.inventory_service.get_inventory_summary()
            
            # Get all bills for analysis
            all_bills = self.billing_service.get_all_bills()
            
            # Calculate top product
            product_sales = {}
            for bill in all_bills:
                for item in bill.items:
                    if item.product_name not in product_sales:
                        product_sales[item.product_name] = 0
                    product_sales[item.product_name] += item.quantity
            
            top_product = max(product_sales.items(), key=lambda x: x[1]) if product_sales else ("N/A", 0)
            
            # Update metric labels
            self.todays_sales_label.config(text=f"${today_summary['total_sales']:.2f}")
            self.total_bills_label.config(text=str(today_summary['total_bills']))
            self.low_stock_items_label.config(text=str(inventory_summary['low_stock_count']))
            self.inventory_value_label.config(text=f"${inventory_summary['total_inventory_value']:.2f}")
            self.top_product_label.config(text=top_product[0])
            self.avg_bill_value_label.config(text=f"${today_summary['average_bill_value']:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def update_sales_chart(self):
        """Update the sales trend chart"""
        try:
            self.sales_ax.clear()
            
            # Get last 7 days of sales data
            dates = []
            sales = []
            
            for i in range(7):
                date = datetime.now() - timedelta(days=6-i)
                summary = self.billing_service.get_daily_sales_summary(date)
                dates.append(date.date())
                sales.append(summary['total_sales'])
            
            # Plot sales trend
            self.sales_ax.plot(dates, sales, marker='o', linewidth=2, markersize=6, color='#2E8B57')
            self.sales_ax.set_title('Daily Sales Trend', fontsize=12, fontweight='bold')
            self.sales_ax.set_xlabel('Date')
            self.sales_ax.set_ylabel('Sales ($)')
            self.sales_ax.grid(True, alpha=0.3)

            # Format x-axis dates
            self.sales_ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            self.sales_ax.xaxis.set_major_locator(mdates.DayLocator())
            # Rotate tick labels and align to avoid overlap
            for lbl in self.sales_ax.get_xticklabels():
                lbl.set_rotation(45)
                lbl.set_ha('right')

            # Use draw_idle so Tkinter can batch redraws when resizing
            self.sales_canvas.draw_idle()
            
        except Exception as e:
            logger.error(f"Error updating sales chart: {e}")
    
    def update_inventory_chart(self):
        """Update the inventory status chart"""
        try:
            self.inventory_ax.clear()
            
            # Get inventory data by category
            products = self.inventory_service.get_all_products()
            categories = {}

            # inventory_service.get_all_products() may return a list
            products_iter = (
                products.values() if hasattr(products, 'values') else products
            )

            for product in products_iter:
                if product.category not in categories:
                    categories[product.category] = {'total': 0, 'low_stock': 0}
                categories[product.category]['total'] += 1
                if product.quantity < product.min_stock_level:
                    categories[product.category]['low_stock'] += 1
            
            # Create pie chart
            labels = list(categories.keys())
            sizes = [categories[cat]['total'] for cat in labels]
            colors = [
                '#2E8B57', '#FF6B6B', '#4ECDC4',
                '#45B7D1', '#96CEB4', '#FFEAA7'
            ]

            wedges, texts, autotexts = self.inventory_ax.pie(
                sizes,
                labels=labels,
                colors=colors[: len(labels)],
                autopct='%1.1f%%',
                startangle=90,
            )
            
            self.inventory_ax.set_title(
                'Inventory by Category', fontsize=12, fontweight='bold'
            )
            
            # Add low stock indicators
            low_stock_text = "\nLow Stock Items:\n"
            for cat in categories:
                if categories[cat]['low_stock'] > 0:
                    low_stock_text += (
                        f"{cat}: {categories[cat]['low_stock']}\n"
                    )
            
            # Place low-stock annotation inside the axes to avoid layout overflow
            self.inventory_ax.text(
                0.95,
                0.5,
                low_stock_text,
                transform=self.inventory_ax.transAxes,
                fontsize=8,
                verticalalignment='center',
                horizontalalignment='left',
            )

            # Draw using draw_idle to play nicely with Tk event loop and resizing
            self.inventory_canvas.draw_idle()
            
        except Exception as e:
            logger.error(f"Error updating inventory chart: {e}")
    
    def update_analytics(self):
        """Update the analytics tabs"""
        try:
            self.update_customer_analytics()
            self.update_product_analytics()
            self.update_predictive_analytics()
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    def update_customer_analytics(self):
        """Update customer analytics"""
        try:
            all_bills = self.billing_service.get_all_bills()

            # Customer analysis
            customer_data = {}
            for bill in all_bills:
                customer_name = bill.customer.name
                if customer_name not in customer_data:
                    customer_data[customer_name] = {
                        'bills': 0,
                        'total_spent': 0,
                        'last_visit': bill.created_at,
                    }
                customer_data[customer_name]['bills'] += 1
                customer_data[customer_name]['total_spent'] += (
                    bill.total_amount
                )
                if bill.created_at > customer_data[customer_name]['last_visit']:
                    customer_data[customer_name]['last_visit'] = (
                        bill.created_at
                    )
            
            # Sort by total spent
            top_customers = sorted(
                customer_data.items(),
                key=lambda x: x[1]['total_spent'],
                reverse=True,
            )[:10]
            
            analytics_text = "TOP CUSTOMERS (by Total Spent)\n"
            analytics_text += "=" * 50 + "\n"
            
            for i, (name, data) in enumerate(top_customers, 1):
                analytics_text += (
                    "{idx:2d}. {name:<20} ${spent:>8.2f} ({bills} bills)\n".format(
                        idx=i,
                        name=name,
                        spent=data['total_spent'],
                        bills=data['bills'],
                    )
                )

            analytics_text += "\nCUSTOMER INSIGHTS\n"
            analytics_text += "=" * 50 + "\n"
            analytics_text += f"Total Customers: {len(customer_data)}\n"
            total_customers = len(customer_data)
            total_bills = (
                sum(d['bills'] for d in customer_data.values())
                if total_customers > 0
                else 0
            )
            total_spent = (
                sum(d['total_spent'] for d in customer_data.values())
                if total_customers > 0
                else 0.0
            )

            avg_bills = (
                total_bills / total_customers
            ) if total_customers > 0 else 0
            avg_spend = (
                total_spent / total_customers
            ) if total_customers > 0 else 0.0

            analytics_text += f"Average Bills per Customer: {avg_bills:.1f}\n"
            analytics_text += f"Average Spend per Customer: ${avg_spend:.2f}\n"
            
            self.customer_metrics_text.delete('1.0', tk.END)
            self.customer_metrics_text.insert('1.0', analytics_text)
            
        except Exception as e:
            logger.error(f"Error updating customer analytics: {e}")
    
    def update_product_analytics(self):
        """Update product performance analytics"""
        try:
            all_bills = self.billing_service.get_all_bills()
            
            # Product analysis
            product_data = {}
            for bill in all_bills:
                for item in bill.items:
                    if item.product_name not in product_data:
                        product_data[item.product_name] = {
                            'quantity': 0,
                            'revenue': 0,
                            'bills': 0,
                        }

                    # always increment totals
                    product_data[item.product_name]['quantity'] += item.quantity
                    product_data[item.product_name]['revenue'] += item.total_price
                    product_data[item.product_name]['bills'] += 1

            # Sort by revenue
            top_products = sorted(
                product_data.items(), key=lambda x: x[1]['revenue'], reverse=True
            )[:10]

            analytics_text = "TOP PERFORMING PRODUCTS\n"
            analytics_text += "=" * 60 + "\n"
            analytics_text += (
                "{prod:<25} {qty:<10} {rev:<12} {bills:<8}\n".format(
                    prod='Product', qty='Qty Sold', rev='Revenue', bills='Bills'
                )
            )
            analytics_text += "-" * 60 + "\n"

            for name, data in top_products:
                analytics_text += (
                    "{name:<25} {qty:<10} ${rev:<11.2f} {bills:<8}\n".format(
                        name=name,
                        qty=data['quantity'],
                        rev=data['revenue'],
                        bills=data['bills'],
                    )
                )

            # Inventory health
            inventory_summary = self.inventory_service.get_inventory_summary()
            analytics_text += "\nINVENTORY HEALTH\n"
            analytics_text += "=" * 60 + "\n"
            analytics_text += (
                "Total Products: {tp}\n".format(
                    tp=inventory_summary['total_products']
                )
            )
            analytics_text += (
                "Low Stock Items: {ls}\n".format(
                    ls=inventory_summary['low_stock_count']
                )
            )
            analytics_text += (
                "Total Inventory Value: ${val:.2f}\n".format(
                    val=inventory_summary['total_inventory_value']
                )
            )
            analytics_text += (
                "Stock Health: {sh}\n".format(sh=inventory_summary['stock_health'])
            )
            
            self.product_metrics_text.delete('1.0', tk.END)
            self.product_metrics_text.insert('1.0', analytics_text)
            
        except Exception as e:
            logger.error(f"Error updating product analytics: {e}")
    
    def update_predictive_analytics(self):
        """Update AI-powered predictive analytics"""
        try:
            # Simple demand forecasting based on recent sales
            all_bills = self.billing_service.get_all_bills()
            
            # Get last 30 days of data
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_bills = [bill for bill in all_bills if bill.created_at >= thirty_days_ago]
            
            # Product demand analysis
            product_demand = {}
            for bill in recent_bills:
                for item in bill.items:
                    if item.product_name not in product_demand:
                        product_demand[item.product_name] = []
                    product_demand[item.product_name].append(item.quantity)
            
            # Calculate average daily demand
            daily_demand = {}
            for product, quantities in product_demand.items():
                daily_demand[product] = sum(quantities) / 30  # Average per day
            
            # Predict next week's needs
            predictions_text = "PREDICTIONS\n"
            predictions_text += "=" * 60 + "\n"
            predictions_text += "DEMAND FORECASTING (Next 7 Days)\n"
            predictions_text += "-" * 60 + "\n"
            
            top_predictions = sorted(daily_demand.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for product, avg_daily in top_predictions:
                predicted_weekly = avg_daily * 7
                predictions_text += f"{product:<25} {predicted_weekly:>8.1f} units\n"
            
            # Low stock predictions
            predictions_text += "\nSTOCK-OUT RISK ANALYSIS\n"
            predictions_text += "-" * 60 + "\n"
            
            products = self.inventory_service.get_all_products()

            # inventory_service.get_all_products() may return a list or a dict
            products_iter = (
                products.values() if hasattr(products, 'values') else products
            )

            for product in products_iter:
                if product.name in daily_demand:
                    days_remaining = (
                        product.quantity / daily_demand[product.name]
                        if daily_demand[product.name] > 0
                        else float('inf')
                    )
                    if days_remaining < 7:
                        predictions_text += (
                            "{name}: {days:.1f} days remaining\n".format(
                                name=product.name, days=days_remaining
                            )
                        )
            
            # Revenue prediction
            recent_revenue = sum(bill.total_amount for bill in recent_bills)
            avg_daily_revenue = recent_revenue / 30
            predicted_weekly_revenue = avg_daily_revenue * 7
            
            predictions_text += "\nREVENUE FORECAST\n"
            predictions_text += "-" * 60 + "\n"
            predictions_text += (
                "Next 7 Days: ${val:.2f}\n".format(
                    val=predicted_weekly_revenue
                )
            )
            predictions_text += (
                "Next 30 Days: ${val:.2f}\n".format(
                    val=avg_daily_revenue * 30
                )
            )
            
            self.ai_predictions_text.delete('1.0', tk.END)
            self.ai_predictions_text.insert('1.0', predictions_text)
            
        except Exception as e:
            logger.error(f"Error updating predictive analytics: {e}")
