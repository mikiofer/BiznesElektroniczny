<?php
/**
 * Copyright since 2007 PrestaShop SA and Contributors
 * PrestaShop is an International Registered Trademark & Property of PrestaShop SA
 *
 * NOTICE OF LICENSE
 *
 * This source file is subject to the Open Software License (OSL 3.0)
 * that is bundled with this package in the file LICENSE.md.
 * It is also available through the world-wide-web at this URL:
 * https://opensource.org/licenses/OSL-3.0
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@prestashop.com so we can send you a copy immediately.
 *
 * DISCLAIMER
 *
 * Do not edit or add to this file if you wish to upgrade PrestaShop to newer
 * versions in the future. If you wish to customize PrestaShop for your
 * needs please refer to https://devdocs.prestashop.com/ for more information.
 *
 * @author    PrestaShop SA and Contributors <contact@prestashop.com>
 * @copyright Since 2007 PrestaShop SA and Contributors
 * @license   https://opensource.org/licenses/OSL-3.0 Open Software License (OSL 3.0)
 */
class AuthControllerCore extends FrontController
{
    public $ssl = true;
    public $php_self = 'authentication';
    public $auth = false;

    public function checkAccess()
    {
        if ($this->context->customer->isLogged() && !$this->ajax) {
            $this->redirect_after = ($this->authRedirection) ? urlencode($this->authRedirection) : 'my-account';
            $this->redirect();
        }

        return parent::checkAccess();
    }

    public function initContent()
    {
        $should_redirect = false;

        if (Tools::isSubmit('submitCreate') || Tools::isSubmit('create_account')) {
            $register_form = $this
                ->makeCustomerForm()
                ->setGuestAllowed(false)
                ->fillWith(Tools::getAllValues());

            if (Tools::isSubmit('submitCreate')) {
                $hookResult = array_reduce(
                    Hook::exec('actionSubmitAccountBefore', [], null, true),
                    function ($carry, $item) {
                        return $carry && $item;
                    },
                    true
                );
                if ($hookResult && $register_form->submit()) {
                    $should_redirect = true;
                }
            }

            $this->context->smarty->assign([
                'register_form' => $register_form->getProxy(),
                'hook_create_account_top' => Hook::exec('displayCustomerAccountFormTop'),
            ]);
            $this->setTemplate('customer/registration');
        } else {
            $login_form = $this->makeLoginForm()->fillWith(
                Tools::getAllValues()
            );

            if (Tools::isSubmit('submitLogin')) {
                if ($login_form->submit()) {
                    $should_redirect = true;
                }
            }

            $this->context->smarty->assign([
                'login_form' => $login_form->getProxy(),
            ]);
            $this->setTemplate('customer/authentication');
        }

        parent::initContent();

if ($should_redirect && !$this->ajax) {
            $back = rawurldecode(Tools::getValue('back'));
            
            // 1. Ustalamy adres docelowy
            $targetUrl = __PS_BASE_URI__; // Domyślnie strona główna

            if (Tools::urlBelongsToShop($back)) {
                $targetUrl = $back;
            } elseif ($this->authRedirection) {
                $targetUrl = $this->authRedirection;
            }

            // 2.Jeśli to była rejestracja, doklejamy parametr
            if (Tools::isSubmit('submitCreate')) {
                // Sprawdzamy, czy w linku jest już znak zapytania
                $separator = (strpos($targetUrl, '?') === false) ? '?' : '&';
                $targetUrl .= $separator . 'registered=true';
            }

            // 3. Wykonujemy przekierowanie na ustalony adres
            return $this->redirectWithNotifications($targetUrl);
        }
    }

    public function getBreadcrumbLinks()
    {
        $breadcrumb = parent::getBreadcrumbLinks();

        if (Tools::isSubmit('submitCreate') || Tools::isSubmit('create_account')) {
            $breadcrumb['links'][] = [
                'title' => $this->trans('Create an account', [], 'Shop.Theme.Customeraccount'),
                'url' => $this->context->link->getPageLink('authentication'),
            ];
        } else {
            $breadcrumb['links'][] = [
                'title' => $this->trans('Log in to your account', [], 'Shop.Theme.Customeraccount'),
                'url' => $this->context->link->getPageLink('authentication'),
            ];
        }

        return $breadcrumb;
    }
}
